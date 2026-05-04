import json
from pathlib import Path
from typing import Any, Dict

from src.indexer import tokenise


DEFAULT_INDEX_PATH = Path("data/index.json")


def save_index(index: Dict[str, Any], file_path: Path = DEFAULT_INDEX_PATH) -> None:
    """
    Save the inverted index to the file system as JSON.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(index, file, indent=2)


def load_index(file_path: Path = DEFAULT_INDEX_PATH) -> Dict[str, Any]:
    """
    Load a previously saved inverted index from the file system.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"No index file found at {file_path}. Run the build command first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_word_entry(index: Dict[str, Any], word: str) -> Dict[str, Any]:
    """
    Return the inverted index entry for a single word.
    """
    tokens = tokenise(word)

    if not tokens:
        return {}

    return index.get(tokens[0], {})


def find_pages(index: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Find pages containing all query terms.

    For multi-word queries, only pages containing every query term are returned.
    """
    query_terms = tokenise(query)

    if not query_terms:
        return {}

    matching_pages = None

    for term in query_terms:
        term_entry = index.get(term, {})
        pages_for_term = set(term_entry.keys())

        if matching_pages is None:
            matching_pages = pages_for_term
        else:
            matching_pages = matching_pages.intersection(pages_for_term)

    if not matching_pages:
        return {}

    results = {}

    for page in matching_pages:
        results[page] = {
            term: index[term][page]
            for term in query_terms
            if page in index.get(term, {})
        }

    return results