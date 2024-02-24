# 初始化一个空字典，用于存储房间号和对应的URL
unique_rooms = {}

# 读取URL_config.ini文件
with open('URL_config_new.ini', 'r', encoding='utf-8') as file:
    for line in file:
        # 分割字符串以获取房间号和主播名
        parts = line.split(',')
        # 获取房间号（URL的最后一部分）
        room_id = parts[0].split('/')[-1]
        # 如果房间号不在字典中，则添加到字典
        if room_id not in unique_rooms:
            unique_rooms[room_id] = line.strip()

# 写入去重后的结果到新文件
with open('URL_config_deduplicated.ini', 'w', encoding='utf-8') as file:
    for url in unique_rooms.values():
        file.write(url + '\n')

print("URL_config_deduplicated.ini文件已生成，并完成去重。")

