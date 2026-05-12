#import all necessary imports
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

#function to fetch HTML for each website
def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    #adds error message if network request fails
    try:
        #add limit to waiting time and return status code if unsuccessful
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        #output failed network error
        print(f"Failed to fetch {url}: {error}")
        return None

#extract the quotes and metadata
def parse_quotes(html: str, page_url: str) -> List[Dict[str, object]]:
    #use beautiful soup (section 1c of the brief) to crawl the page
    soup = BeautifulSoup(html, "html.parser")
    quote_blocks = soup.select("div.quote")

    #store the quotes
    quotes = []

    #loops through the quotes to collect the data (text, author, tag)
    for block in quote_blocks:
        quote_text = block.select_one("span.text")
        author = block.select_one("small.author")
        tags = block.select("a.tag")

        #store the page url, quote text, author, and tags in quotes
        quotes.append(
            {
                "url": page_url,
                "quote": quote_text.get_text(strip=True) if quote_text else "",
                "author": author.get_text(strip=True) if author else "",
                "tags": [tag.get_text(strip=True) for tag in tags],
            }
        )

    return quotes

#find the next page URL
def get_next_page_url(html: str, current_url: str) -> Optional[str]:
    #link to beautiful soup and parse the HTML
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")

    #if the there is no next url, then all the pages have been crawled
    if not next_link:
        return None

    return urljoin(current_url, next_link.get("href"))


#crawls the website using pagination
def crawl_site(
    start_url: str = "https://quotes.toscrape.com/",
    delay_seconds: int = 6,
) -> List[Dict[str, object]]:
    current_url = start_url
    all_quotes = []

    #loops until there is no next page url
    while current_url:
        html = fetch_page(current_url)

        #if the page is not found then stop
        if html is None:
            break
        
        # extract all quotes and find next page url
        page_quotes = parse_quotes(html, current_url)
        all_quotes.extend(page_quotes)

        next_url = get_next_page_url(html, current_url)
    
        #this is the crawler only waits if another request is due
        if next_url:
            #there is a 6 seconds delay for the politeness window (section 1b of brief)
            time.sleep(delay_seconds)

        current_url = next_url

    return all_quotes