from utils.data_sources.social_media.weibo_date_range import Weibo_Date_Range
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# cookie配置
cookies = [
    {
        "domain": ".weibo.com",
        "name": "SUB",
        "value": "_2A25KSageDeRhGeFK41UR8CnNyDSIHXVpJqXWrDV8PUNbmtAGLUrdkW9NQsxdjihvaWTDZwIu9d_cTLWk9FwfdHjw"
    },
    {
        "domain": ".weibo.com",
        "name": "SUBP",
        "value": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhP9T_8KW.B3AJxgJkxqEuI5NHD95QNShnNeh5NeKeRWs4Dqcjli--fi-8siKnXqg8yqg8y"
    }
]

# 创建下载器实例并下载数据
downloader = Weibo_Date_Range(cookies)
df = downloader.download_date_range_stock(
    stock="步步高 股票",  # 搜索关键词
    pages=2,      # 要下载的页数
    delay=2       # 请求间隔时间(秒)
)

print(df)
