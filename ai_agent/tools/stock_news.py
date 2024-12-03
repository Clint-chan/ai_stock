from langchain.tools import tool
from utils.data_sources.news.eastmoney_streaming import Eastmoney_Streaming
from typing import Optional, Union, Dict

@tool
def get_stock_news(query: Union[str, Dict]) -> str:
    """
    获取指定股票代码的最新新闻信息。

    参数:
    query: str 或 dict - 股票代码（例如："002251"）或包含参数的字典

    返回:
    str - 格式化的新闻信息文本
    """
    try:
        # 处理输入参数
        if isinstance(query, dict):
            stock_code = query.get("stock_code", "")
            pages = query.get("pages", 3)
            limit = query.get("limit", 10)
        else:
            # 从查询字符串中提取股票代码
            stock_code = query.replace("股票", "").replace("的新闻", "").strip()
            pages = 3
            limit = 10

        if not stock_code:
            return "请提供有效的股票代码"

        # 配置参数
        config = {
            "max_retry": 3,
            "request_delay": 0.5
        }

        # 初始化下载器并获取数据
        news_downloader = Eastmoney_Streaming(config)
        news_downloader.download_streaming_stock(stock_code, pages)

        # 获取结果
        df = news_downloader.dataframe
        if df is not None and not df.empty:
            # 只保留需要的列并重命名
            news_df = df[["title", "create time"]].copy()
            news_df.columns = ["新闻标题", "发布时间"]

            # 限制显示条数
            news_df = news_df.head(limit)

            # 构建返回信息
            result = (
                f"股票{stock_code}最新新闻（显示{limit}条，共{len(df)}条）：\n"
                f"----------------------------------------\n"
                f"{news_df.to_string(index=False)}\n"
                f"----------------------------------------"
            )
            return result
        else:
            return f"未获取到股票 {stock_code} 的新闻数据"

    except Exception as e:
        return f"获取新闻时发生错误: {str(e)}"