import json
import sys

def add_or_update_record(room_id, name):
    updated = False
    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            # 检查房间号是否存在
            for record in data:
                if record['id'] == room_id:
                    record['name'] = name  # 更新名称
                    updated = True
                    break
            if not updated:
                # 如果房间号不存在，则添加新记录
                data.append({
                    "id": room_id,
                    "name": name,
                    "auto_record": True,
                    "record_danmu": True,
                    "important": False
                })
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return updated

def delete_record(room_id):
    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            # 过滤掉需要删除的房间记录
            data = [record for record in data if record['id'] != room_id]
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")

if __name__ == "__main__":
    file_path = 'rooms.json'  # JSON 文件路径

    if len(sys.argv) == 4 and sys.argv[1] == "add":
        room_id = sys.argv[2]
        name = sys.argv[3]
        updated = add_or_update_record(room_id, name)
        if updated:
            print(f"已存在同房间号，已更新名称为：{name}")
        else:
            print(f"已添加记录：名称 {name}, 房间号 {room_id}")
    elif len(sys.argv) == 3 and sys.argv[1] == "del":
        room_id = sys.argv[2]
        delete_record(room_id)
        print(f"已删除房间号为 {room_id} 的记录。")
    else:
        print("用法：\n添加或更新：python room.py add 房间号 名字\n删除：python script.py del 房间号")
