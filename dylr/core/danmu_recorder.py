import _thread  # 用于启动心跳线程
import gzip  # 用于解压缩 WebSocket 传输的数据
import os  # 提供了与操作系统相关的功能，用于创建目录和文件
import time  # 提供了与时间相关的功能，如时间戳转换等
import traceback  # 用于打印异常的堆栈信息

import websocket  # 用于 WebSocket 连接
from google.protobuf import json_format  # 用于处理 Google Protobuf 格式的数据

from dylr.core import dy_api, app  # 引入其他模块
from dylr.core.dy_protocol import PushFrame, Response, ChatMessage  # 引入自定义协议相关类
from dylr.util import logger, cookie_utils  # 引入其他工具类

class DanmuRecorder:
    def __init__(self, room, room_real_id, start_time=None):
        """
        初始化弹幕录制器
        :param room: 房间信息对象
        :param room_real_id: 房间真实 ID
        :param start_time: 录制开始时间，默认为当前时间
        """
        self.room = room
        self.room_id = room.room_id
        self.room_name = room.room_name
        self.room_real_id = room_real_id
        self.start_time = start_time
        self.ws = None
        self.stop_signal = False
        self.danmu_amount = 0
        self.last_danmu_time = 0
        self.retry = 0

    def start(self):
        """
        开始录制弹幕
        """
        if self.start_time is None:
            self.start_time = time.localtime()
        self.start_time_t = int(time.mktime(self.start_time))
        logger.info_and_print(f'开始录制 {self.room_name}({self.room_id}) 的弹幕')

        # 创建保存文件的目录
        if not os.path.exists("download"):
            os.mkdir("download")
        if not os.path.exists("download/" + self.room_name):
            os.mkdir("download/" + self.room_name)

        start_time_str = time.strftime('%Y%m%d_%H%M%S', self.start_time)
        self.filename = f"download/{self.room_name}/{start_time_str}.xml"
        # 写入文件头部数据
        with open(self.filename, 'w', encoding='UTF-8') as file:
            file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                       "<i>\n")
        self.ws = websocket.WebSocketApp(
            url=dy_api.get_danmu_ws_url(self.room_id, self.room_real_id),
            header=dy_api.get_request_headers(), cookie=cookie_utils.cookie_cache,
            on_message=self._onMessage, on_error=self._onError, on_close=self._onClose,
            on_open=self._onOpen,
        )
        self.ws.run_forever()

    def stop(self):
        """
        停止录制弹幕
        """
        self.stop_signal = True

    def _onOpen(self, ws):
        """
        WebSocket 连接打开时的回调函数
        启动心跳线程
        """
        _thread.start_new_thread(self._heartbeat, (ws,))

    def _onMessage(self, ws: websocket.WebSocketApp, message: bytes):
        """
        接收到消息时的回调函数
        解析并处理消息，将弹幕内容写入文件
        """
        wssPackage = PushFrame()
        wssPackage.ParseFromString(message)
        logid = wssPackage.logid
        decompressed = gzip.decompress(wssPackage.payload)
        payloadPackage = Response()
        payloadPackage.ParseFromString(decompressed)

        # 发送ack包
        if payloadPackage.needAck:
            obj = PushFrame()
            obj.payloadType = 'ack'
            obj.logid = logid
            obj.payloadType = payloadPackage.internalExt
            data = obj.SerializeToString()
            ws.send(data, websocket.ABNF.OPCODE_BINARY)
        # 处理消息
        for msg in payloadPackage.messagesList:
            if msg.method == 'WebcastChatMessage':
                chatMessage = ChatMessage()
                chatMessage.ParseFromString(msg.payload)
                data = json_format.MessageToDict(chatMessage, preserving_proto_field_name=True)
                now = time.time()
                second = now - self.start_time_t
                self.danmu_amount += 1
                self.last_danmu_time = now
                user = data['user']['nickName']
                content = data['content']
                # 写入单条数据
                with open(self.filename, 'a', encoding='UTF-8') as file:
                    time_str = time.strftime('%H:%M:%S', time.gmtime(second))
                    file.write(f"  <d t=\"{time_str}\" user=\"{user}\">{content}</d>\n")

    def _heartbeat(self, ws: websocket.WebSocketApp):
        """
        心跳线程函数
        发送心跳包，检测是否需要重新连接或停止录制
        """
        t = 9
        while True:
            if app.stop_all_threads or self.stop_signal:
                ws.close()
                break
            if not ws.keep_running:
                break
            if t % 10 == 0:
                obj = PushFrame()
                obj.payloadType = 'hb'
                data = obj.SerializeToString()
                ws.send(data, websocket.ABNF.OPCODE_BINARY)
                # 没弹幕，重新连接
                if self.retry < 3 and self.danmu_amount == 0 and t > 30:
                    ws.close()
                    logger.warning_and_print(f'{self.room_name}({self.room_id}) 无法获取弹幕，正在重试({self.retry+1})')
                now = time.time()
                # 太长时间没弹幕，检测是否是下播了，可能下播后并没有断开 websocket
                if t > 30 and now - self.last_danmu_time > 60:
                    if not dy_api.is_going_on_live(self.room):
                        ws.close()
            t += 1
            time.sleep(1)

    def _onError(self, ws, error):
        """
        WebSocket 出错时的回调函数
        打印异常信息
        """
        logger.error_and_print(f'[onError] {self.room_name}({self.room_id}) 弹幕录制抛出一个异常')
        logger.error_and_print(traceback.format_exc())

    def _onClose(self, ws, a, b):
        """
        WebSocket 连接关闭时的回调函数
        完成录制文件的写入，并根据需要重试连接
        """
        # 写入文件尾
        with open(self.filename, 'a', encoding='UTF-8') as file:
            file.write('</i>')
        logger.info_and_print(f'{self.room_name}({self.room_id}) 弹幕录制结束')
        if app.stop_all_threads:
            return
        if self.retry < 10 and dy_api.is_going_on_live(self.room):
            self.retry += 1
            logger.info_and_print(f'{self.room_name}({self.room_id}) 弹幕录制重试({self.retry})')
            self.start_time = None
            time.sleep(1)
            self.start()

