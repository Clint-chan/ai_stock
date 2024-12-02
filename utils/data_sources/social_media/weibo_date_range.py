import os
import json
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import requests
import logging
import time
from tqdm import tqdm
from urllib.parse import quote


class Weibo_Date_Range:
    """微博搜索数据下载器"""

    def __init__(self, cookies):
        """
        初始化下载器
        Args:
            cookies: list, cookie列表
        """
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": self._format_cookies(cookies)  # 直接使用传入的cookies
        }
        self.dataframe = None

    def _format_cookies(self, cookies):
        """格式化cookies"""
        if isinstance(cookies, list):
            return '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        return cookies

    def download_date_range_stock(self, stock, pages=2, delay=2):
        """
        下载指定股票的微博数据
        Args:
            stock: str, 股票名称或关键词
            pages: int, 要下载的页数
            delay: int, 每次请求间隔时间(秒)
        """
        logging.info(f"开始下载 {stock} 的微博数据...")

        results = []
        encoded_stock = quote(stock)

        for page in tqdm(range(1, pages + 1), desc="下载进度"):
            url = f"https://s.weibo.com/weibo?q={encoded_stock}&page={page}"
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()

                page_results = self._parse_page(response.text)
                if page_results:
                    results.extend(page_results)
                    logging.info(f"第 {page} 页找到 {len(page_results)} 条微博")

                if delay > 0 and page < pages:
                    time.sleep(delay)

            except Exception as e:
                logging.error(f"处理第 {page} 页时出错: {str(e)}")
                continue

        if results:
            self.dataframe = pd.DataFrame(results)
            self._save_results(stock)
            return self.dataframe

        return pd.DataFrame()

    def _parse_page(self, html):
        """解析页面内容"""
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='card-wrap')

        results = []
        for card in cards:
            try:
                content = card.find('p', class_='txt')
                if not content:
                    continue

                from_div = card.find('div', class_='from')
                date_link = from_div.find('a') if from_div else None
                user_link = card.find('a', class_='name')

                # 获取互动数据
                interaction = card.find('div', class_='card-act')
                if interaction:
                    items = interaction.find_all('li')
                else:
                    items = []

                post = {
                    'content': content.get_text(strip=True),
                    'date': self._parse_date(date_link.get_text(strip=True)) if date_link else '',
                    'user': user_link.get_text(strip=True) if user_link else '',
                    'reposts': self._parse_number(items[0].get_text(strip=True)) if len(items) > 0 else 0,
                    'comments': self._parse_number(items[1].get_text(strip=True)) if len(items) > 1 else 0,
                    'likes': self._parse_number(items[-1].get_text(strip=True)) if items else 0,
                    'url': 'https://weibo.com' + date_link.get('href', '') if date_link and date_link.get(
                        'href') else ''
                }
                results.append(post)

            except Exception as e:
                logging.warning(f"解析微博卡片时出错: {str(e)}")
                continue

        return results

    def _parse_date(self, date_str):
        """解析日期字符串"""
        try:
            if '分钟前' in date_str:
                minutes = int(date_str.replace('分钟前', ''))
                return (datetime.now() - timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M')
            elif '今天' in date_str:
                time = date_str.replace('今天 ', '')
                return f"{datetime.now().strftime('%Y-%m-%d')} {time}"
            elif '月' in date_str and '日' in date_str:
                return f"2024-{date_str.replace('月', '-').replace('日', '')}"
            return date_str
        except:
            return date_str

    def _parse_number(self, text):
        """解析数字"""
        try:
            if not text or text in ['转发', '评论', '赞']:
                return 0
            text = text.strip()
            if text.isdigit():
                return int(text)
            return 0
        except:
            return 0

    def _save_results(self, stock):
        """保存结果"""
        if self.dataframe is not None and not self.dataframe.empty:
            os.makedirs("News", exist_ok=True)
            filename = f"weibo_{stock}_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath = os.path.join("News", filename)
            self.dataframe.to_csv(filepath, index=False, encoding='utf-8-sig')
            logging.info(f"数据已保存到: {filepath}")