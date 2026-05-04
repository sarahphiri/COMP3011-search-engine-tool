import json
from math import log
from pathlib import Path
from typing import Any, Dict, List, Set

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

def get_all_page_urls(index: Dict[str, Any]) -> Set[str]:
    """
    Return all unique page URLs stored in the inverted index.
    """
    page_urls = set()

    for word_entry in index.values():
        page_urls.update(word_entry.keys())

    return page_urls


def find_pages_ranked(index: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """
    Find pages containing all query terms and rank them using TF-IDF.

    TF-IDF gives a higher score to pages where query terms appear frequently,
    while reducing the influence of terms that appear on many pages.
    """
    query_terms = list(dict.fromkeys(tokenise(query)))

    if not query_terms:
        return []

    matching_pages = None

    for term in query_terms:
        term_entry = index.get(term, {})
        pages_for_term = set(term_entry.keys())

        if not pages_for_term:
            return []

        if matching_pages is None:
            matching_pages = pages_for_term
        else:
            matching_pages = matching_pages.intersection(pages_for_term)

    if not matching_pages:
        return []

    all_pages = get_all_page_urls(index)
    total_documents = len(all_pages)

    if total_documents == 0:
        return []

    ranked_results = []

    for page_url in matching_pages:
        score = 0.0
        term_matches = {}

        for term in query_terms:
            term_data = index[term][page_url]
            term_frequency = term_data["frequency"]
            document_frequency = len(index.get(term, {}))

            inverse_document_frequency = log(
                (total_documents + 1) / (document_frequency + 1)
            ) + 1

            score += term_frequency * inverse_document_frequency
            term_matches[term] = term_data

        ranked_results.append(
            {
                "url": page_url,
                "score": round(score, 4),
                "terms": term_matches,
            }
        )

    return sorted(
        ranked_results,
        key=lambda result: (-result["score"], result["url"]),
    )