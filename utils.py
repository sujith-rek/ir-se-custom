from constants import EMPTY
import tldextract


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


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same domain."""
    extracted1 = tldextract.extract(url1)
    extracted2 = tldextract.extract(url2)
    return extracted1.domain == extracted2.domain and extracted1.suffix == extracted2.suffix
