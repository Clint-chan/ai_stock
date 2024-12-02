import json
import pytz
import time
import requests
import pandas as pd
import numpy as np
from lxml import etree
from tqdm import tqdm
from utils.data_sources.news._base import News_Downloader


class Sina_Finance_Date_Range(News_Downloader):
    def __init__(self, args={}):
        super().__init__(args)
        self.dataframe = pd.DataFrame()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def download_date_range_all(self, start_date, end_date):
        """下载指定日期范围内的所有新闻"""
        self.date_list = pd.date_range(start_date, end_date)
        all_data = []

        for date in tqdm(self.date_list, desc="Downloading Titles..."):
            tmp = self._gather_one_day(date)
            if not tmp.empty:
                all_data.append(tmp)

        if all_data:
            self.dataframe = pd.concat(all_data, ignore_index=True)
            print(f"成功获取 {len(self.dataframe)} 条新闻")
        else:
            print("未获取到任何新闻")

    def _gather_one_day(self, date, delay=0.1):
        """获取指定日期的新闻"""
        # 使用上海时间
        tz = pytz.timezone("Asia/Shanghai")
        end_time = pd.Timestamp(f"{date} 23:59:59").tz_localize(tz)
        start_time = pd.Timestamp(f"{date} 00:00:00").tz_localize(tz)

        end_timestamp = int(end_time.timestamp())
        start_timestamp = int(start_time.timestamp())
        date_str = date.strftime('%Y-%m-%d')

        res = pd.DataFrame()
        for page in range(1, 101):  # 最多获取100页
            url = (f"https://feed.mix.sina.com.cn/api/roll/get?"
                   f"pageid=153&lid=2516&"
                   f"etime={start_timestamp}&stime={end_timestamp}&"
                   f"ctime={end_timestamp}&date={date_str}&"
                   f"k=&num=50&page={page}")

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    print(f"请求失败: {response.status_code}")
                    continue

                data = response.json()
                news_items = data['result']['data']

                if not news_items:
                    break

                # 处理每条新闻
                for item in news_items:
                    df_item = pd.DataFrame([item])
                    res = pd.concat([res, df_item], ignore_index=True)

                time.sleep(delay)

            except Exception as e:
                print(f"处理第 {page} 页时出错: {str(e)}")
                continue

        if not res.empty:
            # 转换时间戳列
            for col in ['ctime', 'mtime', 'intime']:
                if col in res.columns:
                    res[col] = pd.to_datetime(res[col].astype(float), unit='s', utc=True)
                    res[col] = res[col].dt.tz_convert('Asia/Shanghai')

        return res

    def gather_content(self, delay=0.1):
        """获取新闻内容"""
        if self.dataframe.empty:
            print("没有新闻数据需要获取内容")
            return

        self.dataframe['content'] = ''

        with tqdm(total=len(self.dataframe), desc="Gathering news contents") as pbar:
            for idx, row in self.dataframe.iterrows():
                content = self._gather_content_apply(row, pbar, delay)
                self.dataframe.at[idx, 'content'] = content

    def _gather_content_apply(self, x, pbar, delay=0.1):
        """获取单条新闻内容"""
        try:
            response = requests.get(x['url'], headers=self.headers, timeout=10)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                text = response.text
                page = etree.HTML(text)
                content_elements = page.xpath("//*[@id='artibody']/p")
                content = "\n".join([''.join(p.xpath(".//text()")) for p in content_elements])
                content = content.replace("\u3000", "")
                time.sleep(delay)
                pbar.update(1)
                return content
            return np.nan
        except Exception as e:
            print(f"获取内容失败 {x['url']}: {str(e)}")
            return np.nan