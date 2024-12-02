from utils.data_sources.news.sina_finance_date_range import Sina_Finance_Date_Range
from datetime import datetime, timedelta
import os
import pandas as pd

# 创建News文件夹（如果不存在）
news_folder = "News"
if not os.path.exists(news_folder):
    os.makedirs(news_folder)

# 使用精确到分钟的当前时间
now = datetime.now()
one_hour_ago = now - timedelta(minutes=10)

# 格式化时间字符串
start_date = one_hour_ago.strftime("%Y-%m-%d %H:%M")
end_date = now.strftime("%Y-%m-%d %H:%M")

# 生成文件名（用于保存）
file_name = f"sina_news_{start_date.replace(':', '_').replace(' ', '_')}_to_{end_date.replace(':', '_').replace(' ', '_')}.csv"
file_path = os.path.join(news_folder, file_name)

# 基本配置
config = {
    "country": "china",
    "use_proxy": "no",
    "proxy_pages": 0,
    "max_retry": 3,
    "request_delay": 0.5
}

try:
    print(f"开始下载 {start_date} 到 {end_date} 的新闻...")

    # 初始化下载器并获取数据
    news_downloader = Sina_Finance_Date_Range(config)
    news_downloader.download_date_range_all(start_date, end_date)
    news_downloader.gather_content()

    # 获取并显示结果
    df = news_downloader.dataframe
    if df is not None and not df.empty:
        print(f"\n成功获取 {len(df)} 条新闻")

        # 保存数据到CSV文件
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到: {file_path}")

        # 显示预览
        print("\n新闻预览:")
        print(df[["title", "content"]].head())
    else:
        print("未获取到新闻数据")

except Exception as e:
    print(f"发生错误: {str(e)}")
