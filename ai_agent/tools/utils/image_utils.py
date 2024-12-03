import matplotlib.pyplot as plt

def setup_matplotlib():
    """设置matplotlib的全局配置"""
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def display_image(img, title):
    """显示图片的通用函数"""
    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    plt.axis('off')
    plt.title(title, fontsize=12)
    plt.show()
