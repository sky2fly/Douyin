import os
import xml.etree.ElementTree as ET

def seconds_to_hms(seconds):
    """将秒数转换为hh:mm:ss格式"""
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = int(seconds) % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def find_keywords_with_full_content(keywords, directory):
    keywords_count = {keyword: {} for keyword in keywords}  # 初始化每个关键词的计数字典
    for dirpath, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(dirpath, file)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    for elem in root.findall('.//d'):  # 找到所有<d>元素
                        if elem.text:  # 确保元素有文本内容
                            text = elem.text.lower()  # 获取文本内容并转换为小写
                            p_values = elem.get('p').split(',')  # 解析属性值
                            send_time_seconds = float(p_values[0])  # 获取发送时间（秒）
                            send_time_formatted = seconds_to_hms(send_time_seconds)  # 转换发送时间为hh:mm:ss格式
                            for keyword in keywords:
                                if keyword.lower() in text:  # 检查关键词是否在文本中
                                    full_content = elem.text  # 获取完整弹幕内容
                                    log_file = f"{keyword}_search_results_with_content.log"
                                    with open(log_file, "a", encoding="utf-8") as log:
                                        log_entry = f"在文件 {file_path} 中找到 '{keyword}'，发送时间: {send_time_formatted}, 弹幕内容: '{full_content}'\n"
                                        log.write(log_entry)  # 将结果写入日志文件
                                       
                                    key = f"{file_path} @ {send_time_formatted}"
                                    if key not in keywords_count[keyword]:
                                        keywords_count[keyword][key] = 1
                                    else:
                                        keywords_count[keyword][key] += 1
                except ET.ParseError:
                    # 跳过无法解析的文件
                    continue
                except Exception as e:
                    print(f"处理文件 {file_path} 时遇到意外错误: {e}")  # 输出错误信息
                    continue
    # 返回关键词计数结果
    return keywords_count

# 使用示例
keywords = ["关键词1","关键词2"]  # 你要搜索的关键词列表
directory = "."  # 当前目录，可以修改为你需要遍历的目录路径
keywords_counts = find_keywords_with_full_content(keywords, directory)
