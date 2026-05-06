import pytest


@pytest.fixture
def sample_quote_html():
    return """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Life is what happens when you are busy making other plans.”</span>
                <small class="author">Allen Saunders</small>
                <div class="tags">
                    <a class="tag">life</a>
                    <a class="tag">planning</a>
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


@pytest.fixture
def final_quote_html():
    return """
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


@pytest.fixture
def sample_records():
    return [
        {
            "url": "page1",
            "quote": "Life is good",
            "author": "Author One",
            "tags": ["life"],
        },
        {
            "url": "page2",
            "quote": "Good friends matter",
            "author": "Author Two",
            "tags": ["friendship"],
        },
    ]


@pytest.fixture
def sample_index():
    return {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "good": {
            "page1": {"frequency": 1, "positions": [2]},
            "page2": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page2": {"frequency": 1, "positions": [1]},
        },
    }