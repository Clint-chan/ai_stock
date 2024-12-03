from langchain.tools import tool
from utils.data_sources.news.eastmoney_streaming import Eastmoney_Streaming
from typing import Optional, Union, Dict
from pydantic import BaseModel, Field
import json

# 定义输入模型
class StockNewsInput(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    pages: int = Field(default=3, description="获取的页数")
    limit: int = Field(default=10, description="显示的新闻条数")

@tool
def get_stock_news(query: Union[str, Dict, StockNewsInput]) -> str:
    """
    获取指定股票代码的最新新闻信息。

    参数:
        query: 必须包含以下参数：
            - stock_code: 股票代码（必填）
            - pages: 获取的页数（可选，默认3）
            - limit: 显示的新闻条数（可选，默认10）

    示例:
        "query": {
            "stock_code": "002251",
            "pages": 3,
            "limit": 10
            }

    返回:
        str: 格式化的新闻信息文本
    """
    try:
        # 处理输入参数
        if isinstance(query, str):
            # 如果是字符串，尝试解析为字典
            query = json.loads(query)

        if isinstance(query, dict):
            # 如果是字典，转换为StockNewsInput
            query = StockNewsInput(**query)

        stock_code = query.stock_code
        pages = query.pages
        limit = query.limit

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
            news_df = df[["title", "create time"]].copy()
            news_df.columns = ["新闻标题", "发布时间"]
            news_df = news_df.head(limit)

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

# a = get_stock_news.invoke({
#     "query": {
#         "stock_code": "002251",
#         "pages": 3,
#         "limit": 10
#     }
# })
# print(a)