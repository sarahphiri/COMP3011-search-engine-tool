from src.indexer import build_inverted_index, tokenise


def test_tokenise_converts_text_to_lowercase_tokens():
    assert tokenise("Good Friends") == ["good", "friends"]


def test_tokenise_removes_punctuation():
    assert tokenise("Good, friends!") == ["good", "friends"]


def test_build_index_stores_word_frequency():
    records = [
        {
            "url": "https://quotes.toscrape.com/page/1/",
            "quote": "Good friends are good",
            "author": "Example Author",
            "tags": [],
        }
    ]

    index = build_inverted_index(records)

    assert index["good"]["https://quotes.toscrape.com/page/1/"]["frequency"] == 2


def test_build_index_stores_word_positions():
    records = [
        {
            "url": "https://quotes.toscrape.com/page/1/",
            "quote": "Good friends are good",
            "author": "Example Author",
            "tags": [],
        }
    ]

    index = build_inverted_index(records)

    assert index["good"]["https://quotes.toscrape.com/page/1/"]["positions"] == [0, 3]


def test_build_index_handles_multiple_pages():
    records = [
        {
            "url": "https://quotes.toscrape.com/page/1/",
            "quote": "Good friends",
            "author": "Author One",
            "tags": [],
        },
        {
            "url": "https://quotes.toscrape.com/page/2/",
            "quote": "Good choices",
            "author": "Author Two",
            "tags": [],
        },
    ]

    index = build_inverted_index(records)

    assert "https://quotes.toscrape.com/page/1/" in index["good"]
    assert "https://quotes.toscrape.com/page/2/" in index["good"]

def test_tokenise_handles_apostrophes():
    assert tokenise("Don't stop believing.") == ["don't", "stop", "believing"]


def test_tokenise_handles_numbers():
    assert tokenise("Page 2 has 100 quotes") == ["page", "2", "has", "100", "quotes"]


def test_tokenise_returns_empty_list_for_punctuation_only():
    assert tokenise("!!! ... ???") == []


def test_build_index_handles_missing_optional_fields():
    records = [
        {
            "url": "https://quotes.toscrape.com/page/1/",
        }
    ]

    index = build_inverted_index(records)

    assert index == {}


def test_build_index_handles_empty_records_list():
    assert build_inverted_index([]) == {}