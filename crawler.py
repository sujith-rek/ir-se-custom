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

    def extract_links(self, html, base_url) -> list:
        pass

    def normalize_html(self, html) -> str:
        pass

    def crawl(self, url):
        pass


class WebCrawler(Crawler):
    def __init__(self, depth=1) -> None:
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

        html = html.replace("\n", " ")
        html = html.replace("\t", " ")
        html = html.replace("\r", " ")

        return html

    def __is_censored(self, url) -> bool:
        """
        Check if the URL contains any words from the censor list
        :param url: URL to be checked
        :return: True if URL contains censored words, False otherwise
        """
        for censored_word in CENSOR_LIST:
            if censored_word.lower() in url.lower():
                return True
        return False

    def crawl(self, url) -> dict:
        self._crawl_recursive(url, 0, is_main_url=True)
        self._cleanup_link_map()  # Cleanup step to remove 'document': None entries
        return self.link_map

    def _crawl_recursive(self, url, current_depth, is_main_url=False) -> None:
        if current_depth > self.depth or url in self.visited:
            return

        try:
            # Parse the domain of the current URL
            parent_domain = urlparse(url).netloc

            # Skip if the URL contains censored words
            if self.__is_censored(url):
                print(f"Skipping censored link: {url}")
                return

            response = requests.get(url)
            html = response.text
            self.visited.add(url)

            print("Crawling:", url, "Depth:", current_depth)

            # Store normalized content only for the main URL
            document = self.normalize_html(html) if is_main_url else None
            links = self.extract_links(html, url)

            # Initialize the map entry for this URL with document only if it's the main URL
            self.link_map[url] = {
                "document": document,
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

    def _cleanup_link_map(self):
        """
        Remove 'document' keys with None values from link_map
        """
        for url, data in self.link_map.items():
            try:
                if data["document"] is None:
                    del data["document"]
            except KeyError:
                pass