import json

# 定义一个空列表来存储房间信息
rooms = []

# 从URL_config.ini文件读取URL
with open('URL_config.ini', 'r', encoding='utf-8') as file:
    for line in file:
        # 从每一行中解析出房间ID和主播名字
        parts = line.split(',')
        room_id = parts[0].split('/')[-1]
        name = parts[1].split(':')[1].strip()
        
        # 将解析出的信息添加到rooms列表
        rooms.append({'id': room_id, 'name': name})

# 将rooms列表保存到rooms.json文件
with open('rooms_new.json', 'w', encoding='utf-8') as file:
    json.dump(rooms, file, ensure_ascii=False, indent=4)

print("rooms.json文件已生成。")
