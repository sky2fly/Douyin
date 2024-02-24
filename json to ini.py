import json

# 读取rooms.json文件
with open('rooms.json', 'r', encoding='utf-8') as file:
    rooms = json.load(file)

# 打开一个新文件写入转换后的格式
with open('URL_config.ini', 'w', encoding='utf-8') as file:
    for room in rooms:
        # 根据房间信息格式化URL
        url = f"https://live.douyin.com/{room['id']},主播: {room['name']}\n"
        file.write(url)

print("URL_config.ini文件已生成。")
