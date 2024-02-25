import json

# 初始化一个空列表存放房间信息
rooms = []

# 读取URL_config.ini文件中的URL
with open('URL_config.ini', 'r', encoding='utf-8') as file:
    for line in file:
        # 解析房间ID和主播名称
        parts = line.split(',')
        room_id = parts[0].split('/')[-1]
        name = parts[1].split(':')[1].strip()

        # 添加房间信息到列表，包括默认的其他字段
        rooms.append({
            "id": room_id,
            "name": name,
            "auto_record": True,
            "record_danmu": True,
            "important": False
        })

# 将列表信息保存到rooms.json文件
with open('rooms_new.json', 'w', encoding='utf-8') as file:
    json.dump(rooms, file, ensure_ascii=False, indent=4)

print("rooms_new.json文件已生成。")
