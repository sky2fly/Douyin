import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import glob
import os
from lxml import etree

# 设置图表字体为微软雅黑，以支持中文
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 获取当前脚本文件所在的文件夹路径
current_folder = os.path.dirname(os.path.abspath(__file__))
xml_files = glob.glob(os.path.join(current_folder, "*.xml"))

def analyze_xml_file(file_path):
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()

    times = [float(d.get('p').split(',')[0]) for d in root.iter('d') if 'p' in d.attrib and ',' in d.get('p')]
    if not times:  # 检查times列表是否为空
        total_duration = 1  # 防止除以0，可以根据实际情况调整
    else:
        total_duration = max(times)

    time_positions = np.array([time / total_duration for time in times]) if times else np.array([])

    kde = gaussian_kde(time_positions) if times else None
    density = kde(time_positions) if kde else np.array([])
    density_normalized = (density - density.min()) / (density.max() - density.min()) if times else np.array([])

    fig, ax = plt.subplots()
    cmap = plt.cm.jet  # 使用jet颜色映射
    scatter = ax.scatter(time_positions, np.zeros(len(times)), s=density_normalized * 50, c=density_normalized, cmap=cmap, alpha=0.6) if times else None

    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = scatter.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        time_sec = times[ind["ind"][0]]
        text = f'{int(time_sec//3600):02d}:{int((time_sec%3600)//60):02d}:{int(time_sec%60):02d}'
        annot.set_text(text)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax and scatter:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    if scatter:  # 如果存在散点图，则连接hover事件
        fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.title(f'弹幕时间分布散点图 - {os.path.basename(file_path)}')
    plt.xlabel('时间（相对）')
    plt.ylabel('弹幕密度（示意）')
    plt.xticks([])
    plt.yticks([])

    return fig  # 返回创建的figure对象

figs = [analyze_xml_file(xml_file) for xml_file in xml_files if xml_file.endswith('.xml')]  # 分析每个文件并收集figure对象

def on_close(event):
    plt.close('all')  # 当任何一个窗口关闭时关闭所有窗口

for fig in figs:
    fig.canvas.mpl_connect('close_event', on_close)

plt.show()
