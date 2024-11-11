from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()

OPEN_SEARCH_API_KEY = os.getenv("OPEN_SEARCH_API_KEY")
OPEN_SEARCH_CX = os.getenv("OPEN_SEARCH_CX")
OPEN_SEARCH_BASE_URL = os.getenv("OPEN_SEARCH_BASE_URL")
OPEN_SEARCH_ENDPOINT = os.getenv("OPEN_SEARCH_ENDPOINT")
YACY_BASE_URL = os.getenv("YACY_BASE_URL")
YACY_ENDPOINT = os.getenv("YACY_ENDPOINT")


class SearchEngine:
    def __init__(self, base_url, endpoint):
        self.base_url = base_url
        self.endpoint = endpoint

    def parse_query(self, query):
        pass

    def search(self, query):
        pass


class SearchEngineYaCy(SearchEngine):

    def __init__(self):
        super().__init__(YACY_BASE_URL, YACY_ENDPOINT)

    def parse_query(self, query):
        query = query.replace(" ", "+")
        return f"{self.base_url}{self.endpoint}?query={query}&former={query}&maximumRecords=500&resource=global"

    def search(self, query):
        query = self.parse_query(query)

        response = requests.get(query)
        response = json.loads(response.text)

        return response


class SearchEngineOpenSearch(SearchEngine):

    def __init__(self):
        super().__init__(OPEN_SEARCH_BASE_URL, OPEN_SEARCH_ENDPOINT)
        self.cx = OPEN_SEARCH_CX
        self.api_key = OPEN_SEARCH_API_KEY

    def parse_query(self, query):
        return f"{self.base_url}{self.endpoint}?key={self.api_key}&cx={self.cx}&q={query}"

    def search(self, query):
        query = self.parse_query(query)

        collection = []
        for i in range(1, 11):
            next_query = query + "&count=" + str(i * 10) + "&start=" + str(i * 10 + 1)
            collection.append(next_query)

        all_items = []

        for query in collection:
            response = requests.get(query)
            response = json.loads(response.text)
            try:
                items = response["items"]
                all_items.extend(items)
                time.sleep(1)
            except KeyError:
                pass

        return all_items
