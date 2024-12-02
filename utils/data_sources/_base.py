import requests


class FinNLP_Downloader:
    def __init__(self, args={}):
        """初始化下载器
        Args:
            args (dict): 配置参数
        """
        self.max_retry = args.get("max_retry", 1)

    def _request_get(self, url, headers=None, verify=None, params=None):
        """发送GET请求
        Args:
            url (str): 请求URL
            headers (dict, optional): 请求头
            verify (bool, optional): 是否验证SSL证书
            params (dict, optional): URL参数
        Returns:
            requests.Response: 响应对象
        """
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
            }

        response = None
        for _ in range(self.max_retry):
            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    verify=verify,
                    params=params
                )
                if response.status_code == 200:
                    break
            except:
                response = None

        if response is not None and response.status_code != 200:
            response = None

        return response

    def _request_post(self, url, headers, json):
        """发送POST请求
        Args:
            url (str): 请求URL
            headers (dict): 请求头
            json (dict): POST数据
        Returns:
            requests.Response: 响应对象
        """
        response = None
        for _ in range(self.max_retry):
            try:
                response = requests.post(
                    url=url,
                    headers=headers,
                    json=json
                )
                if response.status_code == 200:
                    break
            except:
                response = None

        if response is not None and response.status_code != 200:
            response = None

        return response
