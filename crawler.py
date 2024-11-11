import requests
import re
from urllib.parse import urljoin, urlparse
from censor import get_censor_list, get_skip_types

LINKS_REGEX = r'<a\s+(?:[^>]*?\s+)?href=["\'](https?://[^"\']+)["\']'
SCRIPT_REGEX = r'<script.*?</script>'
STYLE_REGEX = r'<style.*?</style>'
TAGS_REGEX = r'<.*?>'
EMPTY = ''

CENSOR_LIST = get_censor_list()
SKIP_LIST = get_skip_types()


class Crawler:
    def __init__(self):
        pass

    def extract_links(self, html, base_url) -> list:
        pass

    def normalize_html(self, html) -> str:
        pass

    def crawl(self, urls):
        pass


class WebCrawler(Crawler):
    def __init__(self, depth=1):
        super().__init__()
        self.depth = depth
        self.visited = set()
        self.link_map = {}
        self.robots_cache = {}

    def extract_links(self, html, base_url) -> list:
        links = []
        for link in re.findall(LINKS_REGEX, html):
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

    def __is_censored(self, url):
        for censored_word in CENSOR_LIST:
            if censored_word.lower() in url.lower():
                return True
        return False

    def __is_skip_type(self, url):
        """Check if the URL ends with a file type that should be skipped."""
        return any(url.lower().endswith(ext) for ext in SKIP_LIST)

    def __fetch_robots_txt(self, domain):
        """
        Fetch and parse robots.txt rules for the given domain.
        :param domain: The domain to fetch robots.txt for
        :return: A set of disallowed paths
        """
        robots_url = f"http://{domain}/robots.txt"
        disallowed_paths = set()

        try:
            response = requests.get(robots_url)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.strip().lower().startswith("disallow:"):
                        path = line.split(":", 1)[1].strip()
                        if path:
                            disallowed_paths.add(path)
            else:
                print(f"No robots.txt found for domain: {domain}")
        except requests.RequestException as e:
            print(f"Error fetching robots.txt for {domain}: {e}")

        return disallowed_paths

    def __is_allowed_by_robots(self, url):
        """
        Check if the URL is allowed by robots.txt rules.
        :param url: URL to check against robots.txt
        :return: True if allowed, False if disallowed
        """
        domain = urlparse(url).netloc

        if domain not in self.robots_cache:
            self.robots_cache[domain] = self.__fetch_robots_txt(domain)

        disallowed_paths = self.robots_cache[domain]
        path = urlparse(url).path

        for disallowed in disallowed_paths:
            if path.startswith(disallowed):
                print(f"Skipping URL due to robots.txt disallow: {url}")
                return False
        return True

    def crawl(self, urls) -> dict:
        for url in urls:
            if url not in self.visited:
                self._crawl_recursive(url, 0, is_main_url=True)

        self._cleanup_link_map()
        return self.link_map

    def _crawl_recursive(self, url, current_depth, is_main_url=False) -> None:
        if current_depth > self.depth or url in self.visited:
            return
        print("Crawling:", url, "Depth:", current_depth)
        try:
            # Parse the domain of the current URL
            parent_domain = urlparse(url).netloc

            # Skip if the URL contains censored words or is a skip type
            if self.__is_censored(url):
                print(f"Skipping censored link: {url}")
                return
            if self.__is_skip_type(url):
                print(f"Skipping file link (skip type): {url}")
                return

            response = requests.get(url)
            html = response.text
            self.visited.add(url)

            document = self.normalize_html(html) if is_main_url else None
            links = self.extract_links(html, url)

            self.link_map[url] = {
                "document": document,
                "sub_links": []
            }

            for link in links:
                child_domain = urlparse(link).netloc

                # Check if link is allowed by robots.txt
                # if not self.__is_allowed_by_robots(link):
                #     continue

                if child_domain != parent_domain:
                    self._crawl_recursive(link, current_depth + 1)
                    self.link_map[url]["sub_links"].append(link)
                else:
                    print(f"Skipping link (same domain): {link}")

        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")

    def _cleanup_link_map(self):
        for url, data in list(self.link_map.items()):
            try:
                if data["document"] is None:
                    del data["document"]
            except KeyError:
                pass
