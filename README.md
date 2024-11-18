# IR PROJECT

## Introduction

This Project is a simple search engine that uses pagerank algorithm over yacy search engine to rank the search results and provide the user with the most relevant results.

## Installation

```bash
pip install -r requirements.txt
```

## Modules

### Search Engine - `engine.py`

`SearchEngine` is the wrapper class that provides the user with method `search` which takes string argument query and returns the search results.

### Crawler - `crawler.py`

`Crawler` is the wrapper class that provides with methods

- `extract_links` which takes html content as string and returns the list of links in the content.
- `normalize_html` extracts the text from html withou any tags.
- `crawl` takes a list of urls and crawls them to extract the text and links from the pages.

### Graph - `graph.py`

- `DomainGraph` generates the network graph using methods `draw_from_file` and `draw_from_json` that draws using a json file or direct json object respectively. we also have `return_graph_matrix` that returns the adjacency matrix of the graph.
- `PageRank` is the class that provides the user with methods
  - `normalize_matrix` that calculates and creates the normalized matrix of the graph.
  - `calculate_pagerank` that calculates the pagerank of the graph.
  - `get_pagerank` that returns the pagerank of the graph.
  - `display_pagerank` that displays the pagerank of the graph.

### Pre-Processor - `preprocessor.py`

- `Preprocessor` class that gives the method `preprocess` that takes a string and returns tokens that are processed and cleaned with stopwords removed, stemming and lemmatization.

### Vector Space - `vector_space.py`

`VectorSpace` class helps us with the methods `set_docs` that sets the documents and creates index on it. `search` method that takes query tokens and returns the results

### Utils - `utils.py`

- `extract_documents_from_crawled_data` extracts the documents from the crawled json data.
- `is_same_domain` checks if the two urls are from the same domain.
