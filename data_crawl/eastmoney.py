# /data_crawl/eastmoney.py
from utils.data_sources.news.eastmoney_streaming import Eastmoney_Streaming
from datetime import datetime
import os
import pandas as pd

# 创建News文件夹（如果不存在）
news_folder = "News"
if not os.path.exists(news_folder):
    os.makedirs(news_folder)

# 配置参数
pages = 3
stock = "002251"  # 步步高
config = {
    "max_retry": 3,
    "request_delay": 0.5
}

# 生成文件名
now = datetime.now()
file_name = f"eastmoney_{stock}_{now.strftime('%Y%m%d_%H%M')}.csv"
file_path = os.path.join(news_folder, file_name)

try:
    print(f"开始下载股票 {stock} 的新闻数据（{pages}页）...")

    # 初始化下载器并获取数据
    news_downloader = Eastmoney_Streaming(config)
    news_downloader.download_streaming_stock(stock, pages)

    # 获取并显示结果
    df = news_downloader.dataframe
    if df is not None and not df.empty:
        print(f"\n成功获取 {len(df)} 条新闻")

        # 保存数据到CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到: {file_path}")

        # 显示预览
        print("\n新闻预览:")
        print(df[["title", "create time"]].head())
    else:
        print("未获取到新闻数据")

except Exception as e:
    print(f"发生错误: {str(e)}")
