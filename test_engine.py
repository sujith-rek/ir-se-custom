from engines import SearchEngineYaCy, SearchEngineOpenSearch
import json


def test_search_engine_yacy():
    engine = SearchEngineYaCy()
    query = "page rank algorithm"
    response = engine.search(query)
    file = open("test_yacy.json", "w")
    file.write(json.dumps(response, indent=4))
    file.close()


def test_search_engine_open():
    engine = SearchEngineOpenSearch()
    query = "cat in the box"
    response = engine.search(query)
    file = open("test_open.json", "w")
    file.write(json.dumps(response, indent=4))
    file.close()


# test_search_engine_yacy()
test_search_engine_open()
