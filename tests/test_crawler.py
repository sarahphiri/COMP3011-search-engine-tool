from src.crawler import get_next_page_url, parse_quotes


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


def test_parse_quotes_extracts_quote_text():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert len(results) == 2
    assert results[0]["quote"] == "“The world as we have created it is a process of our thinking.”"
    assert results[1]["quote"] == "“It is our choices that show what we truly are.”"


def test_parse_quotes_extracts_authors():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["author"] == "Albert Einstein"
    assert results[1]["author"] == "J.K. Rowling"


def test_parse_quotes_extracts_tags():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["tags"] == ["change", "thinking"]
    assert results[1]["tags"] == ["choices"]


def test_parse_quotes_stores_page_url():
    results = parse_quotes(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert results[0]["url"] == "https://quotes.toscrape.com/"
    assert results[1]["url"] == "https://quotes.toscrape.com/"


def test_get_next_page_url_returns_absolute_url():
    next_url = get_next_page_url(SAMPLE_HTML, "https://quotes.toscrape.com/")

    assert next_url == "https://quotes.toscrape.com/page/2/"


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