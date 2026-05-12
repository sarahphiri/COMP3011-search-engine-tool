import requests

from src.crawler import crawl_site, fetch_page, get_next_page_url, parse_quotes

#sample HTML used for tests by acting as an example page
SAMPLE_HTML = """
<html>
    <body>
        <div class="quote">
            <span class="text">“The world as we have created it is a process of our thinking.”</span>
            <small class="author">Albert Einstein</small>
            <div class="tags">
                <a class="tag">change</a>
                <a class="tag">thinking</a>
            </div>
        </div>

        <div class="quote">
            <span class="text">“It is our choices that show what we truly are.”</span>
            <small class="author">J.K. Rowling</small>
            <div class="tags">
                <a class="tag">choices</a>
            </div>
        </div>

        <nav>
            <ul class="pager">
                <li class="next">
                    <a href="/page/2/">Next</a>
                </li>
            </ul>
        </nav>
    </body>
</html>
"""

#sample HTML for the final page
FINAL_QUOTE_HTML = """
<html>
    <body>
        <div class="quote">
            <span class="text">“Good friends, good books, and a sleepy conscience.”</span>
            <small class="author">Mark Twain</small>
            <div class="tags">
                <a class="tag">friends</a>
                <a class="tag">books</a>
            </div>
        </div>
    </body>
</html>
"""

#acts as a fake response as an example
class MockResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None

#test the quotes are extracted correctly
def test_parse_quotes_extracts_quote_text():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert len(results) == 2
    assert results[0]["quote"] == "“The world as we have created it is a process of our thinking.”"
    assert results[1]["quote"] == "“It is our choices that show what we truly are.”"

#tests names are extracted
def test_parse_quotes_extracts_authors():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["author"] == "Albert Einstein"
    assert results[1]["author"] == "J.K. Rowling"

#tests the tags are extracted
def test_parse_quotes_extracts_tags():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["tags"] == ["change", "thinking"]
    assert results[1]["tags"] == ["choices"]

#test urls are extracted
def test_parse_quotes_stores_page_url():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["url"] == "https://quotes.toscrape.com/"
    assert results[1]["url"] == "https://quotes.toscrape.com/"

#test that next page is extracted
def test_get_next_page_url_returns_absolute_url():
    next_url = get_next_page_url(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert next_url == "https://quotes.toscrape.com/page/2/"

#test can get the url when theres no link
def test_get_next_page_url_returns_none_when_no_next_link():
    html_without_next = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Final quote.”</span>
                <small class="author">Example Author</small>
            </div>
        </body>
    </html>
    """

    next_url = get_next_page_url(
        html_without_next,
        "https://quotes.toscrape.com/page/10/",
    )

    assert next_url is None

#test that empty html doesn't cause a crash
def test_parse_quotes_returns_empty_list_for_empty_html():
    results = parse_quotes("", "https://quotes.toscrape.com/")

    assert results == []

#test that missing fields are handled
def test_parse_quotes_handles_missing_author_and_tags():
    html = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“A quote without author or tags.”</span>
            </div>
        </body>
    </html>
    """

    results = parse_quotes(html, "https://quotes.toscrape.com/")

    assert len(results) == 1
    assert results[0]["quote"] == "“A quote without author or tags.”"
    assert results[0]["author"] == ""
    assert results[0]["tags"] == []

#tesst missing fields are handled safely
def test_parse_quotes_handles_missing_quote_text():
    html = """
    <html>
        <body>
            <div class="quote">
                <small class="author">Unknown Author</small>
                <a class="tag">example</a>
            </div>
        </body>
    </html>
    """

    results = parse_quotes(html, "https://quotes.toscrape.com/")

    assert len(results) == 1
    assert results[0]["quote"] == ""
    assert results[0]["author"] == "Unknown Author"
    assert results[0]["tags"] == ["example"]

#test doesnt crash when given empty html
def test_get_next_page_url_handles_empty_html():
    next_url = get_next_page_url("", "https://quotes.toscrape.com/")

    assert next_url is None

#test html is returned when the request is successful
def test_fetch_page_returns_html_when_request_successful(monkeypatch):
    def fake_get(url, timeout):
        assert url == "https://quotes.toscrape.com/"
        assert timeout == 10
        return MockResponse("<html>Success</html>")

    monkeypatch.setattr("src.crawler.requests.get", fake_get)

    result = fetch_page("https://quotes.toscrape.com/")

    assert result == "<html>Success</html>"

#tests that nothing is returned
def test_fetch_page_returns_none_when_request_fails(monkeypatch):
    def fake_get(url, timeout):
        raise requests.RequestException("Network error")

    monkeypatch.setattr("src.crawler.requests.get", fake_get)

    result = fetch_page("https://quotes.toscrape.com/")

    assert result is None

#tests if politeness window works
def test_crawl_site_observes_six_second_politeness_window(monkeypatch):
    start_url = "https://quotes.toscrape.com/"
    page_two_url = "https://quotes.toscrape.com/page/2/"

    html_by_url = {
        start_url: SAMPLE_HTML,
        page_two_url: FINAL_QUOTE_HTML,
    }

    events = []

    def fake_fetch_page(url):
        events.append(("fetch", url))
        return html_by_url[url]

    def fake_sleep(seconds):
        events.append(("sleep", seconds))

    monkeypatch.setattr("src.crawler.fetch_page", fake_fetch_page)
    monkeypatch.setattr("src.crawler.time.sleep", fake_sleep)

    results = crawl_site(start_url=start_url, delay_seconds=6)

    assert events == [
        ("fetch", start_url),
        ("sleep", 6),
        ("fetch", page_two_url),
    ]

    assert len(results) == 3
    assert results[0]["author"] == "Albert Einstein"
    assert results[1]["author"] == "J.K. Rowling"
    assert results[2]["author"] == "Mark Twain"