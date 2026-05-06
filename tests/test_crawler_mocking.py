import requests

from src.crawler import crawl_site, fetch_page


class MockResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None


def test_fetch_page_returns_html_when_request_successful(monkeypatch):
    def fake_get(url, timeout):
        assert url == "https://quotes.toscrape.com/"
        assert timeout == 10
        return MockResponse("<html>Success</html>")

    monkeypatch.setattr("src.crawler.requests.get", fake_get)

    result = fetch_page("https://quotes.toscrape.com/")

    assert result == "<html>Success</html>"


def test_fetch_page_returns_none_when_request_fails(monkeypatch):
    def fake_get(url, timeout):
        raise requests.RequestException("Network error")

    monkeypatch.setattr("src.crawler.requests.get", fake_get)

    result = fetch_page("https://quotes.toscrape.com/")

    assert result is None


def test_crawl_site_follows_pagination_without_real_requests(
    monkeypatch,
    sample_quote_html,
    final_quote_html,
):
    start_url = "https://quotes.toscrape.com/"
    page_two_url = "https://quotes.toscrape.com/page/2/"

    html_by_url = {
        start_url: sample_quote_html,
        page_two_url: final_quote_html,
    }

    requested_urls = []
    sleep_calls = []

    def fake_fetch_page(url):
        requested_urls.append(url)
        return html_by_url[url]

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr("src.crawler.fetch_page", fake_fetch_page)
    monkeypatch.setattr("src.crawler.time.sleep", fake_sleep)

    results = crawl_site(start_url=start_url, delay_seconds=6)

    assert requested_urls == [start_url, page_two_url]
    assert sleep_calls == [6]
    assert len(results) == 2
    assert results[0]["author"] == "Allen Saunders"
    assert results[1]["author"] == "Mark Twain"