import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch the HTML content for a URL.

    Returns the HTML as a string if successful.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        print(f"Failed to fetch {url}: {error}")
        return None


def parse_quotes(html: str, page_url: str) -> List[Dict[str, object]]:
    """
    Extract quote text, author, tags, and source page URL from a page.
    """
    soup = BeautifulSoup(html, "html.parser")
    quote_blocks = soup.select("div.quote")

    quotes = []

    for block in quote_blocks:
        quote_text = block.select_one("span.text")
        author = block.select_one("small.author")
        tags = block.select("a.tag")

        quotes.append(
            {
                "url": page_url,
                "quote": quote_text.get_text(strip=True) if quote_text else "",
                "author": author.get_text(strip=True) if author else "",
                "tags": [tag.get_text(strip=True) for tag in tags],
            }
        )

    return quotes


def get_next_page_url(html: str, current_url: str) -> Optional[str]:
    """
    Find the next page URL from the current page, if one exists.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    if not next_link:
        return None

    return urljoin(current_url, next_link.get("href"))


def crawl_site(
    start_url: str = "https://quotes.toscrape.com/",
    delay_seconds: int = 6,
) -> List[Dict[str, object]]:
    """
    Crawl quotes.toscrape.com, following pagination until no next page exists.

    A delay is applied between successive requests to respect the politeness requirement.
    """
    current_url = start_url
    all_quotes = []

    while current_url:
        html = fetch_page(current_url)

        if html is None:
            break

        page_quotes = parse_quotes(html, current_url)
        all_quotes.extend(page_quotes)

        next_url = get_next_page_url(html, current_url)

        if next_url:
            time.sleep(delay_seconds)

        current_url = next_url

    return all_quotes