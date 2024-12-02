# Juchao
from utils.data_sources.company_announcement.juchao import Juchao_Announcement

start_date = "2020-01-01"
end_date = "2020-06-01"
stock = "002251"
config = {
    "country": "china",
    "use_proxy": "no",
    "proxy_pages": 0,
    "max_retry": 3,
    "request_delay": 0.5
}

downloader = Juchao_Announcement(config)
downloader.download_date_range_stock(start_date, end_date, stock = stock, get_content = True, delate_pdf = True)
selected_columns = ["announcementTime", "shortTitle","Content"]
downloader.dataframe[selected_columns].head(10)