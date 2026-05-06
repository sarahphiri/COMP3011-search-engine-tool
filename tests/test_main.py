from src.main import run_shell


def test_cli_build_find_and_exit_with_mocked_input(monkeypatch, capsys):
    inputs = iter(["build", "find life", "exit"])

    records = [
        {
            "url": "page1",
            "quote": "Life is good",
            "author": "Author One",
            "tags": ["life"],
        }
    ]

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("src.main.crawl_site", lambda: records)
    monkeypatch.setattr("src.main.save_index", lambda index: None)

    run_shell()

    output = capsys.readouterr().out

    assert "Index built and saved" in output
    assert "Ranked pages found for query: 'life'" in output
    assert "Goodbye." in output


def test_cli_load_handles_missing_index_file(monkeypatch, capsys):
    inputs = iter(["load", "exit"])

    def fake_load_index():
        raise FileNotFoundError("No index file found. Run build first.")

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("src.main.load_index", fake_load_index)

    run_shell()

    output = capsys.readouterr().out

    assert "No index file found. Run build first." in output
    assert "Goodbye." in output


def test_cli_unknown_command_shows_help(monkeypatch, capsys):
    inputs = iter(["unknowncommand", "exit"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run_shell()

    output = capsys.readouterr().out

    assert "Unknown command: unknowncommand" in output
    assert "Available commands:" in output