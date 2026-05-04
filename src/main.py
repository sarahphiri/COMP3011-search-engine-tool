from typing import Any, Dict

from src.crawler import crawl_site
from src.indexer import build_inverted_index
from src.search import find_pages, get_word_entry, load_index, save_index


def print_help() -> None:
    """
    Print available commands.
    """
    print("\nAvailable commands:")
    print("  build              Crawl website, build index, and save it")
    print("  load               Load saved index from file")
    print("  print <word>       Print inverted index entry for a word")
    print("  find <query>       Find pages containing query terms")
    print("  help               Show this help message")
    print("  exit               Exit the program\n")


def run_shell() -> None:
    """
    Run the command-line search tool.
    """
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

        if command == "help":
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
            results = find_pages(index, query)

            if not results:
                print(f"No pages found for query: '{query}'")
            else:
                print(f"Pages found for query: '{query}'")
                for page_url, match_data in results.items():
                    print(f"- {page_url}: {match_data}")

        else:
            print(f"Unknown command: {command}")
            print_help()


if __name__ == "__main__":
    run_shell()