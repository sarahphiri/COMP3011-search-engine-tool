import pytest

from src.search import find_pages, get_word_entry, load_index, save_index


def test_save_and_load_index(tmp_path):
    index = {
        "good": {
            "https://quotes.toscrape.com/page/1/": {
                "frequency": 2,
                "positions": [0, 3],
            }
        }
    }

    file_path = tmp_path / "index.json"

    save_index(index, file_path)
    loaded_index = load_index(file_path)

    assert loaded_index == index


def test_load_index_raises_error_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing-index.json"

    with pytest.raises(FileNotFoundError):
        load_index(missing_file)


def test_get_word_entry_returns_entry_for_existing_word():
    index = {
        "good": {
            "https://quotes.toscrape.com/page/1/": {
                "frequency": 1,
                "positions": [0],
            }
        }
    }

    result = get_word_entry(index, "good")

    assert "https://quotes.toscrape.com/page/1/" in result


def test_get_word_entry_is_case_insensitive():
    index = {
        "good": {
            "https://quotes.toscrape.com/page/1/": {
                "frequency": 1,
                "positions": [0],
            }
        }
    }

    result = get_word_entry(index, "GOOD")

    assert "https://quotes.toscrape.com/page/1/" in result


def test_get_word_entry_returns_empty_dict_for_missing_word():
    index = {"good": {}}

    assert get_word_entry(index, "missing") == {}


def test_find_pages_returns_pages_for_single_word():
    index = {
        "good": {
            "https://quotes.toscrape.com/page/1/": {
                "frequency": 1,
                "positions": [0],
            }
        }
    }

    result = find_pages(index, "good")

    assert "https://quotes.toscrape.com/page/1/" in result


def test_find_pages_returns_pages_containing_all_query_terms():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    result = find_pages(index, "good friends")

    assert "page1" in result
    assert "page2" not in result


def test_find_pages_returns_empty_dict_for_empty_query():
    index = {"good": {"page1": {"frequency": 1, "positions": [0]}}}

    assert find_pages(index, "") == {}


def test_find_pages_returns_empty_dict_for_missing_word():
    index = {"good": {"page1": {"frequency": 1, "positions": [0]}}}

    assert find_pages(index, "missing") == {}