import pytest

from src.main import run_shell

from src.search import (
    discover_quotes,
    find_pages,
    find_pages_ranked,
    get_word_entry,
    is_quoted_phrase,
    load_index,
    load_records,
    lucky_quote,
    order_terms_by_document_frequency,
    phrase_search,
    save_index,
    save_records,
    score_quote_record,
    strip_query_quotes,
    suggest_terms,
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

def test_phrase_search_returns_page_when_terms_are_consecutive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    results = phrase_search(index, "good friends")

    assert len(results) == 1
    assert results[0]["url"] == "page1"
    assert results[0]["phrase_positions"] == [0]


def test_phrase_search_does_not_return_page_when_terms_are_not_consecutive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [3]},
        },
    }

    results = phrase_search(index, "good friends")

    assert results == []


def test_phrase_search_requires_all_terms_to_exist():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    results = phrase_search(index, "good friends")

    assert results == []


def test_phrase_search_is_case_insensitive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    results = phrase_search(index, "GOOD FRIENDS")

    assert len(results) == 1
    assert results[0]["url"] == "page1"


def test_phrase_search_handles_punctuation():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    results = phrase_search(index, "good, friends!")

    assert len(results) == 1
    assert results[0]["url"] == "page1"


def test_suggest_terms_returns_close_match_for_missing_word():
    index = {
        "friend": {},
        "life": {},
        "truth": {},
    }

    suggestions = suggest_terms(index, "frend")

    assert "frend" in suggestions
    assert "friend" in suggestions["frend"]


def test_suggest_terms_ignores_existing_words():
    index = {
        "friend": {},
        "life": {},
    }

    suggestions = suggest_terms(index, "friend")

    assert suggestions == {}


def test_suggest_terms_returns_empty_dict_when_no_close_match():
    index = {
        "friend": {},
        "life": {},
    }

    suggestions = suggest_terms(index, "xyzabc")

    assert suggestions == {}


def test_is_quoted_phrase_returns_true_for_quoted_query():
    assert is_quoted_phrase('"good friends"') is True


def test_is_quoted_phrase_returns_false_for_unquoted_query():
    assert is_quoted_phrase("good friends") is False


def test_strip_query_quotes_removes_surrounding_quotes():
    assert strip_query_quotes('"good friends"') == "good friends"

def test_order_terms_by_document_frequency_orders_rarest_terms_first():
    index = {
        "common": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [0]},
            "page3": {"frequency": 1, "positions": [0]},
        },
        "rare": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    ordered_terms = order_terms_by_document_frequency(index, ["common", "rare"])

    assert ordered_terms == ["rare", "common"]

def test_save_and_load_records(tmp_path):
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": ["life"],
        }
    ]

    file_path = tmp_path / "records.json"

    save_records(records, file_path)
    loaded_records = load_records(file_path)

    assert loaded_records == records


def test_load_records_raises_error_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing-records.json"

    with pytest.raises(FileNotFoundError):
        load_records(missing_file)


def test_score_quote_record_rewards_quote_text_match():
    record = {
        "url": "page1",
        "quote": "Life is what happens when you are busy making other plans.",
        "author": "Allen Saunders",
        "tags": ["life", "planning"],
    }

    result = score_quote_record(record, "life")

    assert result["score"] > 0
    assert any("quote text" in reason for reason in result["reasons"])


def test_score_quote_record_rewards_tag_match():
    record = {
        "url": "page1",
        "quote": "A quote about planning.",
        "author": "Example Author",
        "tags": ["life"],
    }

    result = score_quote_record(record, "life")

    assert result["score"] >= 4
    assert any("tag" in reason for reason in result["reasons"])


def test_score_quote_record_rewards_exact_phrase_match():
    record = {
        "url": "page1",
        "quote": "Good friends, good books, and a sleepy conscience.",
        "author": "Mark Twain",
        "tags": ["friends", "books"],
    }

    result = score_quote_record(record, "good friends")

    assert result["score"] >= 5
    assert any("Exact phrase" in reason for reason in result["reasons"])


def test_discover_quotes_returns_top_results_in_score_order():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        },
        {
            "url": "page2",
            "quote": "Life life life.",
            "author": "Author Two",
            "tags": [],
        },
    ]

    results = discover_quotes(records, "life", limit=2)

    assert len(results) == 2
    assert results[0]["record"]["url"] == "page2"


def test_discover_quotes_respects_limit():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        },
        {
            "url": "page2",
            "quote": "Life is interesting.",
            "author": "Author Two",
            "tags": [],
        },
    ]

    results = discover_quotes(records, "life", limit=1)

    assert len(results) == 1


def test_discover_quotes_returns_empty_list_for_missing_query():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        }
    ]

    assert discover_quotes(records, "xyzabc") == []


def test_discover_quotes_returns_empty_list_for_empty_query():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        }
    ]

    assert discover_quotes(records, "") == []


def test_lucky_quote_returns_best_single_result():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        },
        {
            "url": "page2",
            "quote": "Life life life.",
            "author": "Author Two",
            "tags": [],
        },
    ]

    result = lucky_quote(records, "life")

    assert result is not None
    assert result["record"]["url"] == "page2"


def test_lucky_quote_returns_none_when_no_result():
    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": [],
        }
    ]

    assert lucky_quote(records, "xyzabc") is None

def run_cli_with_inputs(monkeypatch, commands):
    """
    Run the CLI with mocked user input.
    """
    inputs = iter(commands)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))


def sample_cli_index():
    return {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }


def sample_cli_records():
    return [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": ["life"],
        }
    ]


def test_cli_build_find_and_exit_with_mocked_input(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["build", "find life", "exit"])

    records = [
        {
            "url": "page1",
            "quote": "Life is good",
            "author": "Author One",
            "tags": ["life"],
        }
    ]

    monkeypatch.setattr("src.main.crawl_site", lambda: records)
    monkeypatch.setattr("src.main.save_index", lambda index: None)
    monkeypatch.setattr("src.main.save_records", lambda records: None)

    run_shell()

    output = capsys.readouterr().out

    assert "Index built and saved" in output
    assert "Ranked pages found for query: 'life'" in output
    assert "Goodbye." in output


def test_cli_load_successfully_loads_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Index loaded. Loaded 1 unique words and 1 quote records." in output
    assert "Goodbye." in output


def test_cli_load_handles_missing_index_file(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "exit"])

    def fake_load_index():
        raise FileNotFoundError("No index file found. Run build first.")

    monkeypatch.setattr("src.main.load_index", fake_load_index)

    run_shell()

    output = capsys.readouterr().out

    assert "No index file found. Run build first." in output
    assert "Goodbye." in output


def test_cli_unknown_command_shows_help(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["unknowncommand", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Unknown command: unknowncommand" in output
    assert "Available commands:" in output


def test_cli_help_command_shows_help(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["help", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Available commands:" in output
    assert "build" in output
    assert "find <query>" in output


def test_cli_empty_command_is_handled(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Please enter a command." in output
    assert "Goodbye." in output


def test_cli_print_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a word" in output


def test_cli_print_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["print life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output


def test_cli_print_existing_word(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print life", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "page1" in output
    assert "frequency" in output


def test_cli_print_missing_word(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print missing", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "No index entry found for 'missing'." in output


def test_cli_find_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output


def test_cli_find_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["find life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output


def test_cli_find_ranked_results(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find life", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 2, "positions": [0, 3]},
            "page2": {"frequency": 1, "positions": [1]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Ranked pages found for query: 'life'" in output
    assert "score" in output


def test_cli_find_missing_query_shows_suggestions(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find frend", "exit"])

    index = {
        "friend": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "life": {
            "page2": {"frequency": 1, "positions": [0]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "No pages found for query: 'frend'" in output
    assert "Suggestions:" in output
    assert "friend" in output


def test_cli_find_quoted_phrase(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", 'find "life is"', "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "is": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Exact phrase matches for: 'life is'" in output
    assert "page1" in output


def test_cli_find_quoted_phrase_no_results(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", 'find "life good"', "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "good": {
            "page1": {"frequency": 1, "positions": [3]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output


def test_cli_phrase_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "phrase", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a phrase" in output


def test_cli_phrase_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["phrase life is", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output


def test_cli_phrase_returns_exact_match(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "phrase life is", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "is": {
            "page1": {"frequency": 1, "positions": [1]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Exact phrase matches for: 'life is'" in output
    assert "page1" in output


def test_cli_phrase_no_results(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "phrase life good", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "good": {
            "page1": {"frequency": 1, "positions": [4]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output


def test_cli_suggest_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "suggest", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output


def test_cli_suggest_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["suggest frend", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output


def test_cli_suggest_returns_suggestions(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "suggest frend", "exit"])

    index = {
        "friend": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "life": {
            "page2": {"frequency": 1, "positions": [0]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Suggestions for: 'frend'" in output
    assert "friend" in output


def test_cli_suggest_no_suggestions(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "suggest xyzabc", "exit"])

    index = {
        "friend": {
            "page1": {"frequency": 1, "positions": [0]},
        },
        "life": {
            "page2": {"frequency": 1, "positions": [0]},
        },
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "No suggestions found for: 'xyzabc'" in output


def test_cli_lucky_returns_best_quote(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["build", "lucky life", "exit"])

    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": ["life"],
        }
    ]

    monkeypatch.setattr("src.main.crawl_site", lambda: records)
    monkeypatch.setattr("src.main.save_index", lambda index: None)
    monkeypatch.setattr("src.main.save_records", lambda records: None)

    run_shell()

    output = capsys.readouterr().out

    assert "I'm Feeling Lucky result for: 'life'" in output
    assert "Life is good." in output
    assert "Discovery score" in output


def test_cli_discover_returns_quote_recommendations(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["build", "discover life", "exit"])

    records = [
        {
            "url": "page1",
            "quote": "Life is good.",
            "author": "Author One",
            "tags": ["life"],
        },
        {
            "url": "page2",
            "quote": "Life is interesting.",
            "author": "Author Two",
            "tags": [],
        },
    ]

    monkeypatch.setattr("src.main.crawl_site", lambda: records)
    monkeypatch.setattr("src.main.save_index", lambda index: None)
    monkeypatch.setattr("src.main.save_records", lambda records: None)

    run_shell()

    output = capsys.readouterr().out

    assert "Quote discovery results for: 'life'" in output
    assert "Life is good." in output
    assert "Discovery score" in output


def test_cli_lucky_requires_query(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "lucky", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output


def test_cli_discover_requires_query(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "discover", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)
    monkeypatch.setattr("src.main.load_records", sample_cli_records)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output


def test_cli_lucky_requires_loaded_records(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["lucky life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No quote records loaded. Run build or load first." in output


def test_cli_discover_requires_loaded_records(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["discover life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No quote records loaded. Run build or load first." in output