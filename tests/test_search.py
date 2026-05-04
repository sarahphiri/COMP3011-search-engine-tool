import pytest

from src.search import (
    find_pages,
    find_pages_ranked,
    get_word_entry,
    load_index,
    save_index,
)

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

def test_get_word_entry_handles_punctuation_in_word():
    index = {
        "good": {
            "page1": {
                "frequency": 1,
                "positions": [0],
            }
        }
    }

    result = get_word_entry(index, "good!")

    assert "page1" in result


def test_find_pages_handles_punctuation_in_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    result = find_pages(index, "good, friends!")

    assert "page1" in result


def test_find_pages_handles_repeated_query_terms():
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]},
        }
    }

    result = find_pages(index, "good good")

    assert "page1" in result


def test_find_pages_is_case_insensitive_for_multi_word_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    result = find_pages(index, "GOOD FRIENDS")

    assert "page1" in result


def test_load_index_raises_error_for_invalid_json(tmp_path):
    invalid_file = tmp_path / "invalid-index.json"
    invalid_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(Exception):
        load_index(invalid_file)

def test_find_pages_ranked_returns_results_for_single_word():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 3, "positions": [0, 2, 5]},
        }
    }

    results = find_pages_ranked(index, "good")

    assert len(results) == 2
    assert results[0]["url"] == "page2"
    assert results[0]["score"] > results[1]["score"]


def test_find_pages_ranked_requires_all_query_terms():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    results = find_pages_ranked(index, "good friends")

    assert len(results) == 1
    assert results[0]["url"] == "page1"


def test_find_pages_ranked_returns_empty_list_for_empty_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    assert find_pages_ranked(index, "") == []


def test_find_pages_ranked_returns_empty_list_for_missing_term():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    assert find_pages_ranked(index, "missing") == []


def test_find_pages_ranked_is_case_insensitive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    results = find_pages_ranked(index, "GOOD")

    assert len(results) == 1
    assert results[0]["url"] == "page1"


def test_find_pages_ranked_handles_punctuation_in_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    results = find_pages_ranked(index, "good, friends!")

    assert len(results) == 1
    assert results[0]["url"] == "page1"