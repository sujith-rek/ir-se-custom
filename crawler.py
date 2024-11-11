import requests
import re
from urllib.parse import urljoin, urlparse
from censor import get_censor_list

LINKS_REGEX = r'<a\s+(?:[^>]*?\s+)?href=["\'](https?://[^"\']+)["\']'
SCRIPT_REGEX = r'<script.*?</script>'
STYLE_REGEX = r'<style.*?</style>'
TAGS_REGEX = r'<.*?>'
EMPTY = ''

CENSOR_LIST = get_censor_list()


class Crawler:
    def __init__(self):
        pass

    def crawl(self, url):
        pass


class WebCrawler(Crawler):
    def __init__(self, depth=1):
        super().__init__()
        self.depth = depth
        self.visited = set()
        self.link_map = {}

    def extract_links(self, html, base_url) -> list:
        links = []
        for link in re.findall(LINKS_REGEX, html):
            # Resolve relative URLs to absolute
            absolute_link = urljoin(base_url, link)
            links.append(absolute_link)
        return links

    def normalize_html(self, html) -> str:
        html = re.sub(SCRIPT_REGEX, EMPTY, html, flags=re.DOTALL)
        html = re.sub(STYLE_REGEX, EMPTY, html, flags=re.DOTALL)
        html = re.sub(TAGS_REGEX, EMPTY, html)
        return html

    def is_censored(self, url):
        """
        Check if the URL contains any words from the censor list
        :param url: URL to be checked
        :return: True if URL contains censored words, False otherwise
        """
        for censored_word in CENSOR_LIST:
            if censored_word.lower() in url.lower():
                return True
        return False

    def crawl(self, url):
        self._crawl_recursive(url, 0)
        return self.link_map

    def _crawl_recursive(self, url, current_depth):
        if current_depth > self.depth or url in self.visited:
            return

        try:
            # Parse the domain of the current URL
            parent_domain = urlparse(url).netloc

            # Skip if the URL contains censored words
            if self.is_censored(url):
                print(f"Skipping censored link: {url}")
                return

            response = requests.get(url)
            html = response.text
            self.visited.add(url)

            print("Crawling:", url, "Depth:", current_depth)

            # Normalize and extract content
            document = self.normalize_html(html)
            links = self.extract_links(html, url)

            # Initialize the sub_links map for this parent URL
            self.link_map[url] = {
                "document": document,
                "links": links,
                "sub_links": []
            }

            # Recursively crawl each link
            for link in links:
                child_domain = urlparse(link).netloc

                # Only proceed if the child domain is different from the parent domain
                if child_domain != parent_domain:
                    self._crawl_recursive(link, current_depth + 1)
                    # Track the sub-links in the parent link's map
                    self.link_map[url]["sub_links"].append(link)
                else:
                    print(f"Skipping link (same domain): {link}")

        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")


# Example usage:
crawler = WebCrawler(depth=2)
result = crawler.crawl(
    "http://localhost:8090/yacysearch.html?query=cat&Enter=&auth=&verify=ifexist&contentdom=text&nav=location%2Chosts%2Cauthors%2Cnamespace%2Ctopics%2Cfiletype%2Cprotocol%2Clanguage&startRecord=0&indexof=off&meanCount=5&resource=global&prefermaskfilter=&maximumRecords=10&timezoneOffset=-330"
)
print("\nCrawling result:")
for parent, data in result.items():
    print(f"{parent}")
    for child in data["sub_links"]:
        print("  |---", child)
