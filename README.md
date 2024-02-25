# 抖音直播录制
## 特点
- 无人值守自动录制
- 支持录制弹幕
- 无需设置cookie
- 支持脚本、插件

## 缺点
- 不支持更改清晰度
- 不支持自动分割

## 添加主播
### 方法1
可以在 GUI 界面中点击下方的 *添加主播* 来添加房间，支持 Web_Sid、直播间地址、直播间短链、(正在直播的)主播主页。

使用纯命令行的用户，可以先在有 GUI 的平台下添加好房间，再把 room.json 复制到纯命令行平台下。或者：

在软件根目录下找到 room.json，用文本编辑器打开它，下面是几个例子：
``` text
[
  {
    "id": 71034333127,
    "name": "主播名1",
    "auto_record": true,
    "record_danmu": true,
    "important": false
  },
  {
    "id": 851917085931,
    "name": "主播名2",
    "auto_record": true,
    "record_danmu": true,
    "important": false
  }
]
```
name 可以填主播名，同时也是录制到的文件所存放的目录名，由于一些主播会经常改名，所以不自动获取名称，你可以自己填一个容易记的名字。

auto_record 是否自动监测和录制，一般是 true，如果不想录了又怕删掉它下次不方便加回来，可以改成 false。

record_danmu 为是否录制弹幕，对性能要求较高，根据实际需求和录制设备性能决定。

important 为 true 的情况下，该主播使用独立线程检测，以保证第一时间录到直播。**不建议添加太多重要主播**。

### 方法2 
添加主播 `python room.py add [房间号] [主播名字]`

删除主播 `python room.py del [房间号]`

## 运行
双击 main.pyw 即可运行 GUI 版。

运行命令行版，Windows 平台直接打开 运行命令行版.bat 就可以了

对于命令行版，当配置或房间修改时，需要重新启动软件才能生效。

下载的文件存放于 *根目录/download* 下。

## 自动转码
需要下载 ffmpeg，可以放在软件根目录下或其他位置，在 config.txt 中配置 ffmpeg 所在目录，并配置自动转码选项。

## 插件
在 src/plugin/plugin.py 中编写你的插件，比如当直播开始时向一个 api POST 一个信息以便通知你开播了：
``` python
def on_live_start(room):
    post(f'123.45.67.89:65565/?room_name={room.room_name}')
```

## 其他工具
路径Tool
- key.py 弹幕关键词查找
- swap.py FLV转MP4
- reli.py 弹幕热力图

## 手动对录制到的文件进行处理

下载到的文件是flv格式，由于时间戳错误等，许多软件播放有异常，可以使用 PotPlayer 播放，但仍存在拖拽进度条卡顿等问题，你可以尝试转码：

下载 ffmpeg 并将其添加到环境变量中(网上有教程)，假设录到的文件名是 *20230114_123456.flv*，执行指令：
``` bash
ffmpeg -i 20230114_123456.flv -c copy 20230114_123456.mp4
```
可以进行无损转码，且速度非常快，还能修复部分由于时间戳错误造成的问题。
如果不嫌转码麻烦费时的话，可以只保留 flv 格式，要用的时候才转为 mp4 格式，以免日后发现转码后的视频有问题时，原flv文件已经删了。

下载的弹幕是类 b站xml 格式的，可以使用 [nicovert](https://github.com/muzuiget/niconvert) 来转为 ass 格式字幕文件，播放时拖入 PotPlayer 就能显示弹幕了。

如果要将弹幕渲染到视频中，可以使用命令：
``` bash
ffmpeg -i 20230114_123456.flv -vf ass=20230114_123456.ass 有弹幕.mp4
```

但是这样如果原视频模糊或帧数低的话，弹幕也会模糊或一卡一卡的，你可以先生成一个高质量中间文件，再渲染弹幕：
``` bash
ffmpeg -i 20230114_123456.flv -c:v h264 -b:v 5824k -vf scale=iw*2:ih*2 -c:a copy -r 60 hq.mp4
ffmpeg -i hq.mp4 -c:v h264 -b:v 5824k -vf ass=20230114_123456.ass -c:a copy 有弹幕.mp4
```

## Linux平台(无图形化界面)安装
如果使用 Linux 应该会安装 python吧。

安装 chrome:
``` bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
安装完后，执行命令
``` bash
google-chrome --version
```
如果能看到版本号，则说明安装成功。

软件会自动安装 chromedriver，如果安装失败，可以：

记住上面命令得到的版本号，执行以下指令以找到相同版本的 chromedriver，下载并放到软件根目录下，并给它运行权限：
``` bash
wget https://chromedriver.storage.googleapis.com/你安装的google-chrome的版本/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo chmod -x chromedriver
```
