from constants import EMPTY


def extract_documents_from_crawled_data(data: dict) -> dict:
    """Extract relevant documents from the crawled data."""
    documents = {}
    for url, details in data.items():
        try:
            document = details["document"]
            if document and document != EMPTY:
                documents[url] = document
        except KeyError:
            pass
    return documents
