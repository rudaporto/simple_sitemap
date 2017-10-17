from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests


class Crawler:
    """Simple crawler to get all internal links from a website."""

    def __init__(self, base_uri):
        """Initialize local data."""
        self.base_uri = base_uri
        self.base_netloc = urlparse(self.base_uri).netloc
        self.to_visit = [base_uri]
        self.visited = []
        self.links = []

    def get(self, uri) -> str:
        """Request data from website."""
        response = requests.get(uri)
        self.to_visit.remove(uri)
        self.visited.append(uri)
        print(f'Link visited: {uri}')
        return response.text

    def filter_links(self, page_links):
        """Verify if the link local and return absolute uri or None"""
        filtered_links = set()
        links_parsed = [urlparse(link) for link in page_links]
        absolute_links = [p for p in links_parsed if p.netloc == self.base_netloc]
        relative_links = [p for p in links_parsed if p.netloc == '' and p.path and p.path != '/']

        for parsed in absolute_links + relative_links:
            new_link = urljoin(self.base_uri, parsed.path)
            if new_link not in self.visited:
                filtered_links.add(new_link)

        filtered_links = list(filtered_links)
        return filtered_links

    def update_links(self):
        """Parse text and update links found and to visit."""
        new_to_visit = set()
        for uri in self.to_visit:
            text = self.get(uri)
            soup = BeautifulSoup(text, 'lxml')
            page_links = [link.get('href') for link in soup.find_all('a')]
            page_links = self.filter_links(page_links)
            for link in page_links:

                if link not in self.links:
                    print(f'New link added: {link}')
                    self.links.append(link)

                if link not in self.to_visit:
                    print(f'New link to visit: {link}')
                    new_to_visit.add(link)

        self.to_visit.extend(list(new_to_visit))

    def run(self):
        """Run the the crawler."""
        while self.to_visit:
            self.update_links()

        return self.links


if __name__ == '__main__':
    # simple site
    crawler = Crawler('https://briefy.co')

    # big site can take ours without
    # crawler = Crawler('https://www.terra.com.br')

    for link in crawler.run():
        print(link)
