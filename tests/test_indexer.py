from src.indexer import build_inverted_index, tokenise

#test that the tokens are lowercase
def test_tokenise_converts_text_to_lowercase_tokens():
    assert tokenise("Good Friends") == ["good", "friends"]

#test that punctuation is removed
def test_tokenise_removes_punctuation():
    assert tokenise("Good, friends!") == ["good", "friends"]

#test that the inverted index stores frequency of the words
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

#test that inverted index stores word positions
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

#test that the same word can be indexed
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

#test that apostrophes are tokenised
def test_tokenise_handles_apostrophes():
    assert tokenise("Don't stop believing.") == ["don't", "stop", "believing"]

#test that numbers are tokens
def test_tokenise_handles_numbers():
    assert tokenise("Page 2 has 100 quotes") == ["page", "2", "has", "100", "quotes"]

#test that no tokens are returned when there is only punctuation
def test_tokenise_returns_empty_list_for_punctuation_only():
    assert tokenise("!!! ... ???") == []

#test that records are handled when they have missing optional fields
def test_build_index_handles_missing_optional_fields():
    records = [
        {
            "url": "https://quotes.toscrape.com/page/1/",
        }
    ]

    index = build_inverted_index(records)

    assert index == {}

#test that empty records creates an empty index
def test_build_index_handles_empty_records_list():
    assert build_inverted_index([]) == {}


#test to check if the crawler does not treat the end of one quote as the start of another
def test_build_index_adds_gap_between_records_on_same_page():
    records = [
        {
            "url": "page1",
            "quote": "good",
            "author": "",
            "tags": [],
        },
        {
            "url": "page1",
            "quote": "friends",
            "author": "",
            "tags": [],
        },
    ]

    index = build_inverted_index(records)

    assert index["good"]["page1"]["positions"] == [0]
    assert index["friends"]["page1"]["positions"] == [2]