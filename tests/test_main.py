from src.main import run_shell


def run_cli_with_inputs(monkeypatch, commands):
    """
    Run the CLI with mocked user input.
    """
    inputs = iter(commands)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))


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


def test_cli_load_successfully_loads_index(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

    run_shell()

    output = capsys.readouterr().out

    assert "Index loaded. Loaded 1 unique words." in output
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

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

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

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

    run_shell()

    output = capsys.readouterr().out

    assert "page1" in output
    assert "frequency" in output


def test_cli_print_missing_word(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "print missing", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

    run_shell()

    output = capsys.readouterr().out

    assert "No index entry found for 'missing'." in output


def test_cli_find_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "find", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

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

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output


def test_cli_phrase_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "phrase", "exit"])

    index = {
        "life": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

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

    run_shell()

    output = capsys.readouterr().out

    assert "No exact phrase matches found for: 'life good'" in output


def test_cli_suggest_requires_argument(monkeypatch, capsys):
    run_cli_with_inputs(monkeypatch, ["load", "suggest", "exit"])

    index = {
        "friend": {
            "page1": {"frequency": 1, "positions": [0]},
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

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

    run_shell()

    output = capsys.readouterr().out

    assert "No suggestions found for: 'xyzabc'" in output