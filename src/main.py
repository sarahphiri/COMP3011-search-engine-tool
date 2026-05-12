from typing import Any, Dict

from src.crawler import crawl_site
from src.indexer import build_inverted_index
from src.search import (
    find_pages_ranked,
    get_word_entry,
    is_quoted_phrase,
    load_index,
    phrase_search,
    save_index,
    strip_query_quotes,
    suggest_terms,
)

#outputs all the commands included in the search engine
def print_help() -> None:
    """
    Print available commands.
    """
    print("\nAvailable commands:")
    print("  build              Crawl website, build index, and save it")
    print("  load               Load saved index from file")
    print("  print <word>       Print inverted index entry for a word")
    print("  find <query>       Find pages containing query terms with TF-IDF ranking")
    print('  find "<phrase>"    Find exact phrase matches using word positions')
    print("  phrase <query>     Find exact phrase matches using word positions")
    print("  suggest <query>    Suggest close indexed terms for a query")
    print("  help               Show this help message")
    print("  exit               Exit the program\n")


#if the user inputs a spelling mistake or words with a close match it will suggest
def print_suggestions(index: Dict[str, Any], query: str) -> None:
    suggestions = suggest_terms(index, query)

    if suggestions:
        print("Suggestions:")
        for missing_term, matches in suggestions.items():
            print(f"- {missing_term}: {', '.join(matches)}")

#outputs the result of the search
def print_discovery_result(result: Dict[str, Any], rank: int | None = None) -> None:
    record = result["record"]
    prefix = f"{rank}. " if rank is not None else ""

    print(f'{prefix}"{record.get("quote", "")}"')
    print(f"— {record.get('author', 'Unknown author')}")
    print(f"Source page: {record.get('url', '')}")

    tags = record.get("tags", [])

    if tags:
        print(f"Tags: {', '.join(tags)}")

    print(f"Discovery score: {result['score']}")

    if result["reasons"]:
        print("Why this matched:")
        for reason in result["reasons"]:
            print(f"- {reason}")

#runs the search tool (depending on the command)
def run_shell() -> None:
    index: Dict[str, Any] = {}

    print("COMP3011 Search Engine Tool")
    print_help()

    while True:
        user_input = input("> ").strip()

        if not user_input:
            print("Please enter a command.")
            continue

        parts = user_input.split()
        command = parts[0].lower()
        arguments = parts[1:]

        if command == "exit":
            print("Goodbye.")
            break

        elif command == "help":
            print_help()

        elif command == "build":
            print("Crawling website and building index...")
            records = crawl_site()
            index = build_inverted_index(records)
            save_index(index)
            print(f"Index built and saved. Indexed {len(index)} unique words.")

        elif command == "load":
            try:
                index = load_index()
                print(f"Index loaded. Loaded {len(index)} unique words.")
            except FileNotFoundError as error:
                print(error)

        elif command == "print":
            if not arguments:
                print("Please provide a word, e.g. print nonsense")
                continue

            if not index:
                print("No index loaded. Run build or load first.")
                continue

            word = arguments[0]
            entry = get_word_entry(index, word)

            if not entry:
                print(f"No index entry found for '{word}'.")
                print_suggestions(index, word)
            else:
                print(entry)

        elif command == "find":
            if not arguments:
                print("Please provide a query, e.g. find good friends")
                continue

            if not index:
                print("No index loaded. Run build or load first.")
                continue

            query = " ".join(arguments)

            if is_quoted_phrase(query):
                phrase = strip_query_quotes(query)
                results = phrase_search(index, phrase)

                if not results:
                    print(f"No exact phrase matches found for: '{phrase}'")
                    print_suggestions(index, phrase)
                else:
                    print(f"Exact phrase matches for: '{phrase}'")
                    for result in results:
                        print(
                            f"- {result['url']} "
                            f"(matches: {result['match_count']}, "
                            f"positions: {result['phrase_positions']})"
                        )

            else:
                results = find_pages_ranked(index, query)

                if not results:
                    print(f"No pages found for query: '{query}'")
                    print_suggestions(index, query)
                else:
                    print(f"Ranked pages found for query: '{query}'")
                    for result in results:
                        print(
                            f"- {result['url']} "
                            f"(score: {result['score']}): "
                            f"{result['terms']}"
                        )

        elif command == "phrase":
            if not arguments:
                print("Please provide a phrase, e.g. phrase good friends")
                continue

            if not index:
                print("No index loaded. Run build or load first.")
                continue

            phrase = " ".join(arguments)
            results = phrase_search(index, phrase)

            if not results:
                print(f"No exact phrase matches found for: '{phrase}'")
                print_suggestions(index, phrase)
            else:
                print(f"Exact phrase matches for: '{phrase}'")
                for result in results:
                    print(
                        f"- {result['url']} "
                        f"(matches: {result['match_count']}, "
                        f"positions: {result['phrase_positions']})"
                    )

        elif command == "suggest":
            if not arguments:
                print("Please provide a query, e.g. suggest frend")
                continue

            if not index:
                print("No index loaded. Run build or load first.")
                continue

            query = " ".join(arguments)
            suggestions = suggest_terms(index, query)

            if not suggestions:
                print(f"No suggestions found for: '{query}'")
            else:
                print(f"Suggestions for: '{query}'")
                for missing_term, matches in suggestions.items():
                    print(f"- {missing_term}: {', '.join(matches)}")

        else:
            print(f"Unknown command: {command}")
            print_help()


if __name__ == "__main__":
    run_shell()