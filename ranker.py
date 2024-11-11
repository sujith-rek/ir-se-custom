from crawler import WebCrawler
from engines import SearchEngineOpenSearch
import json

searcher = SearchEngineOpenSearch(limit=20)
crawler = WebCrawler(depth=1)
query = input("Enter a query: ")
all_data, links = searcher.search(query)
crawled_data = [crawler.crawl(links)]
fil = open("search_results_all.json", "w")
fil.write(json.dumps(all_data, indent=4))
fil.close()

fil = open("search_results_crawled.json", "w")
fil.write(json.dumps(crawled_data, indent=4))
fil.close()
