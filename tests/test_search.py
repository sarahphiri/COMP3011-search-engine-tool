import pytest

from src.main import run_shell

from src.search import (
    find_pages,
    find_pages_ranked,
    get_word_entry,
    is_quoted_phrase,
    load_index,
    order_terms_by_document_frequency,
    phrase_search,
    save_index,
    strip_query_quotes,
    suggest_terms,
)

#test that index can be saved as JSON
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

#test that missing index files causes an error
def test_load_index_raises_error_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing-index.json"

    with pytest.raises(FileNotFoundError):
        load_index(missing_file)

#test returns data for a word in the index
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

#test that capatalisation doesn't affect getting word entry
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

#test that amissing word returns an empty dictionary
def test_get_word_entry_returns_empty_dict_for_missing_word():
    index = {"good": {}}

    assert get_word_entry(index, "missing") == {}

#test that single word querys works (for find_pages)
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

#test that searches for multiple words returns pages containing all terms
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

#test that empty querys doesn't show results
def test_find_pages_returns_empty_dict_for_empty_query():
    index = {"good": {"page1": {"frequency": 1, "positions": [0]}}}

    assert find_pages(index, "") == {}

#test that query terms which are not in the index (or on the website) return nothing
def test_find_pages_returns_empty_dict_for_missing_word():
    index = {"good": {"page1": {"frequency": 1, "positions": [0]}}}

    assert find_pages(index, "missing") == {}

#test that punctuation is removed before words are looked up in index
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

#test that punctuation is removed when searches contain multiple words
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

#test that repeated query terms don't break the search
def test_find_pages_handles_repeated_query_terms():
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]},
        }
    }

    result = find_pages(index, "good good")

    assert "page1" in result

#test that search for multiple words is case insensitive
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

#test than invalid JSON is rejected
def test_load_index_raises_error_for_invalid_json(tmp_path):
    invalid_file = tmp_path / "invalid-index.json"
    invalid_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(Exception):
        load_index(invalid_file)

#test that ranked pages are ordered using TF-IDF
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

#test that ranked searches require all query terms
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

#test that ranked searches handle empty queries
def test_find_pages_ranked_returns_empty_list_for_empty_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    assert find_pages_ranked(index, "") == []

#test that ranked searches return no results when there is a term missing
def test_find_pages_ranked_returns_empty_list_for_missing_term():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    assert find_pages_ranked(index, "missing") == []

#test that find pages is not case sensitive
def test_find_pages_ranked_is_case_insensitive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    results = find_pages_ranked(index, "GOOD")

    assert len(results) == 1
    assert results[0]["url"] == "page1"

#test that rnaked searches remove punctuation
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

#test that searches return pages when the words are next to each other
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

#test that phrase searches reject non-consecutive words
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

#tests that phrase search fails if a term is missing
def test_phrase_search_requires_all_terms_to_exist():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    results = phrase_search(index, "good friends")

    assert results == []

#test that phrase search is not case sensitive
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

#test that punctuation is removed before calculating positions
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

#test that suggestions return close matches to searches which are misspelt
def test_suggest_terms_returns_close_match_for_missing_word():
    index = {
        "friend": {},
        "life": {},
        "truth": {},
    }

    suggestions = suggest_terms(index, "frend")

    assert "frend" in suggestions
    assert "friend" in suggestions["frend"]

#test that suggestions ignore words in the index
def test_suggest_terms_ignores_existing_words():
    index = {
        "friend": {},
        "life": {},
    }

    suggestions = suggest_terms(index, "friend")

    assert suggestions == {}

#test that suggestions return nothing when there is no close match
def test_suggest_terms_returns_empty_dict_when_no_close_match():
    index = {
        "friend": {},
        "life": {},
    }

    suggestions = suggest_terms(index, "xyzabc")

    assert suggestions == {}

#test that quoted queries are recognised as phrase searches
def test_is_quoted_phrase_returns_true_for_quoted_query():
    assert is_quoted_phrase('"good friends"') is True

#test that unquoted queries are not treated as quoted
def test_is_quoted_phrase_returns_false_for_unquoted_query():
    assert is_quoted_phrase("good friends") is False

#test that quote marks are removed from the query
def test_strip_query_quotes_removes_surrounding_quotes():
    assert strip_query_quotes('"good friends"') == "good friends"

#test that rare query terms are ordered before more common terms
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

#test the CLI with fake commands
def run_cli_with_inputs(monkeypatch, commands):
    inputs = iter(commands)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

#returns sample index for CLI tests
def sample_cli_index():
    return {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

#test CLI flow of build, find, and then exit
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

    run_shell()

    output = capsys.readouterr().out

    assert "Index built and saved" in output
    assert "Ranked pages found for query: 'life'" in output
    assert "Goodbye." in output

#test the CLI is loading indexes successfully
def test_cli_load_successfully_loads_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "Index loaded. Loaded 1 unique words." in output
    assert "Goodbye." in output

#test that CLI handles missing index files
def test_cli_load_handles_missing_index_file(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "exit"])

    def fake_load_index():
        raise FileNotFoundError("No index file found. Run build first.")

    monkeypatch.setattr("src.main.load_index", fake_load_index)

    run_shell()

    output = capsys.readouterr().out

    assert "No index file found. Run build first." in output
    assert "Goodbye." in output

#test unknown CLI commands print the commands (help command)
def test_cli_unknown_command_shows_help(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["unknowncommand", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Unknown command: unknowncommand" in output
    assert "Available commands:" in output

#test that help commands prints all commands
def test_cli_help_command_shows_help(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["help", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Available commands:" in output
    assert "build" in output
    assert "find <query>" in output

#tests empty cli commands are handled
def test_cli_empty_command_is_handled(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "Please enter a command." in output
    assert "Goodbye." in output

#test that print command requires an argument as a word
def test_cli_print_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a word" in output

#test that print cannot run before index has been loaded
def test_cli_print_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["print life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output

#test that print command shows existing words
def test_cli_print_existing_word(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print life", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "page1" in output
    assert "frequency" in output

#test that print command reports a missing word
def test_cli_print_missing_word(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print missing", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "No index entry found for 'missing'." in output

#test that find requires a query argument
def test_cli_find_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output

#test that find cannot run before the index is loaded
def test_cli_find_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["find life", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output

#test that the CLI prints ranked results
def test_cli_find_ranked_results(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find life", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 2, "positions": [0, 3]},
            "page2": {"frequency": 1, "positions": [1]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

    run_shell()

    output = capsys.readouterr().out

    assert "Ranked pages found for query: 'life'" in output
    assert "score" in output

#test that missing query shows suggestions
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

    run_shell()

    output = capsys.readouterr().out

    assert "No pages found for query: 'frend'" in output
    assert "Suggestions:" in output
    assert "friend" in output

#test that find queries use exact phrases
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

    run_shell()

    output = capsys.readouterr().out

    assert "Exact phrase matches for: 'life is'" in output
    assert "page1" in output

#test that find says when an exact phrase is not found
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

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output

#test that phrase requires an argument
def test_cli_phrase_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "phrase", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a phrase" in output

#test that phrase doesn't run before an index is loaded
def test_cli_phrase_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["phrase life is", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output

#tests that CLI phrase returns an exact match
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

    run_shell()

    output = capsys.readouterr().out

    assert "Exact phrase matches for: 'life is'" in output
    assert "page1" in output

#test that CLI phrase reports no exact match
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

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output

#test that suggest requires an argument
def test_cli_suggest_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "suggest", "exit"])

    monkeypatch.setattr("src.main.load_index", sample_cli_index)

    run_shell()

    output = capsys.readouterr().out

    assert "Please provide a query" in output

#test that suggest can not run before index is loaded
def test_cli_suggest_requires_loaded_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["suggest frend", "exit"])

    run_shell()

    output = capsys.readouterr().out

    assert "No index loaded. Run build or load first." in output

#test that suggest command returns close matches
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

    run_shell()

    output = capsys.readouterr().out

    assert "Suggestions for: 'frend'" in output
    assert "friend" in output

#test that CLI reports when there are no suggestions
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

    run_shell()

    output = capsys.readouterr().out

    assert "No suggestions found for: 'xyzabc'" in output
