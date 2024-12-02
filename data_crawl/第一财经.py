from finnlp.data_sources.news.yicai_streaming import Yicai_Streaming
news_downloader = Yicai_Streaming()
news_downloader.download_streaming_search(keyword = "步步高", rounds = 3)
selected_columns = ["author", "creationDate", "desc" ,"source", "title"]
print(news_downloader.dataframe[selected_columns].head(10))