import os
import subprocess

# 设置要搜索的文件夹路径
folder_path = './'

# 遍历文件夹及其所有子文件夹
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".flv"):
            video_file = os.path.join(root, file)
            
            # 构建输出文件名（将.flv扩展名更改为.mp4）
            output_file = video_file.rsplit('.', 1)[0] + '.mp4'

            # 构建ffmpeg命令
            ffmpeg_command = [
                'ffmpeg', '-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda', '-i', video_file,
                '-c:v', 'h264_nvenc', '-preset', 'fast', output_file
            ]

            # 执行命令
            subprocess.run(ffmpeg_command)
            print(f'Converted {video_file} to {output_file}')

# 检查是否有文件被转换，由于我们已经遍历了所有的文件，这个检查可能不再必要，但为了脚本完整性，可以保留
converted_files = any(file.endswith(".flv") for root, dirs, files in os.walk(folder_path) for file in files)
if not converted_files:
    print('No .flv files found in the specified folder.')
