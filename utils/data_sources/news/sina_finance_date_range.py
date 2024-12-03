import json
import pytz
import time
import requests
import pandas as pd
import numpy as np
from lxml import etree
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.data_sources.news._base import News_Downloader
from typing import Optional, Dict, List
from datetime import datetime


class Sina_Finance_Date_Range(News_Downloader):
    BASE_URL = "https://feed.mix.sina.com.cn/api/roll/get"
    SHANGHAI_TZ = pytz.timezone("Asia/Shanghai")

    def __init__(self, args: Dict = {}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()

    def _make_request(self, url: str, timeout: int = 10) -> Optional[dict]:
        """发送HTTP请求并处理响应"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"请求失败: {str(e)}")
            return None

    def _process_news_items(self, news_items: List[dict]) -> pd.DataFrame:
        """处理新闻项并转换为DataFrame"""
        if not news_items:
            return pd.DataFrame()

        df = pd.DataFrame(news_items)

        # 转换时间戳列
        time_columns = ['ctime', 'mtime', 'intime']
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col].astype(float), unit='s', utc=True)
                df[col] = df[col].dt.tz_convert(self.SHANGHAI_TZ)

        return df

    def _gather_one_day(self, date: datetime, delay: float = 0.1) -> pd.DataFrame:
        """获取指定日期的新闻"""
        all_news = []

        for page in range(1, 101):  # 最多获取100页
            url = f"{self.BASE_URL}?pageid=153&lid=2516&num=50&page={page}"

            data = self._make_request(url)
            if not data:
                continue

            news_items = data.get('result', {}).get('data', [])
            if not news_items:
                break

            all_news.extend(news_items)
            time.sleep(delay)

        return self._process_news_items(all_news)

    def _fetch_content(self, url: str) -> Optional[str]:
        """获取单个URL的新闻内容"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'

            page = etree.HTML(response.text)
            content_elements = page.xpath("//*[@id='artibody']/p")
            content = "\n".join([''.join(p.xpath(".//text()")) for p in content_elements])
            return content.replace("\u3000", "").strip()
        except Exception as e:
            print(f"\n获取内容失败 {url}: {str(e)}")
            return None

    def gather_content(self, delay: float = 0.1, max_workers: int = 5):
        """并行获取新闻内容"""
        if self.dataframe.empty:
            print("没有新闻数据需要获取内容")
            return

        self.dataframe['content'] = ''
        urls = self.dataframe['url'].tolist()

        print("\n开始获取新闻详细内容...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self._fetch_content, url): url for url in urls}

            for future in tqdm(as_completed(future_to_url), total=len(urls), desc="获取新闻内容"):
                url = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        idx = self.dataframe[self.dataframe['url'] == url].index[0]
                        self.dataframe.at[idx, 'content'] = content
                    time.sleep(delay)
                except Exception as e:
                    print(f"\n处理内容时出错 {url}: {str(e)}")

    def download_date_range_all(self, start_date: str, end_date: str):
        """下载指定日期范围内的所有新闻"""
        start_dt = pd.to_datetime(start_date).tz_localize(self.SHANGHAI_TZ)
        end_dt = pd.to_datetime(end_date).tz_localize(self.SHANGHAI_TZ)

        tmp = self._gather_one_day(start_dt)

        if not tmp.empty:
            mask = (tmp['ctime'] >= start_dt) & (tmp['ctime'] <= end_dt)
            self.dataframe = tmp[mask]

            if not self.dataframe.empty:
                print(f"成功获取 {len(self.dataframe)} 条新闻")
                self.dataframe = self.dataframe.sort_values('ctime', ascending=False)
            else:
                print("在指定时间范围内未获取到新闻")
        else:
            print("未获取到任何新闻")
