import json
from difflib import get_close_matches
from math import log
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

from src.indexer import tokenise

#set location for the inverted index
DEFAULT_INDEX_PATH = Path("data/index.json")

#save the inverted index
def save_index(index: Dict[str, Any], file_path: Path = DEFAULT_INDEX_PATH) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(index, file, indent=2)

#load the inverted index (section 1(d)(ii) of the brief)
def load_index(file_path: Path = DEFAULT_INDEX_PATH) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"No index file found at {file_path}. Run the build command first."
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
    
#return the inverted index for the word being searched
def get_word_entry(index: Dict[str, Any], word: str) -> Dict[str, Any]:
    tokens = tokenise(word)

    if not tokens:
        return {}

    return index.get(tokens[0], {})

#finds the pages which contain the terms in the query (including functionality for multi-word searches - section 1(d)(iv))
def find_pages(index: Dict[str, Any], query: str) -> Dict[str, Any]:
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

#return the URLs in the index
def get_all_page_urls(index: Dict[str, Any]) -> Set[str]:
    page_urls = set()

    for word_entry in index.values():
        page_urls.update(word_entry.keys())

    return page_urls

#finds pages using TF-IDF
def find_pages_ranked(index: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    query_terms = list(dict.fromkeys(tokenise(query)))
    query_terms = order_terms_by_document_frequency(index, query_terms)

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

#checks if the search has double quotation marks
def is_quoted_phrase(query: str) -> bool:
    stripped_query = query.strip()

    return (
        len(stripped_query) >= 2
        and stripped_query[0] == '"'
        and stripped_query[-1] == '"'
    )

#removes surrounding quotation marks from the search
def strip_query_quotes(query: str) -> str:
    return query.strip()[1:-1].strip()

#finds starting positions for each word
def _find_consecutive_phrase_positions(position_lists: List[List[int]]) -> List[int]:
    if not position_lists:
        return []

    if len(position_lists) == 1:
        return position_lists[0]

    following_position_sets = [
        set(positions)
        for positions in position_lists[1:]
    ]

    phrase_start_positions = []

    for start_position in position_lists[0]:
        phrase_matches = True

        for offset, position_set in enumerate(following_position_sets, start=1):
            if start_position + offset not in position_set:
                phrase_matches = False
                break

        if phrase_matches:
            phrase_start_positions.append(start_position)

    return phrase_start_positions

#ensures phrase appears in correct order
def phrase_search(index: Dict[str, Any], phrase: str) -> List[Dict[str, Any]]:
    phrase_terms = tokenise(phrase)

    if not phrase_terms:
        return []

    filter_terms = order_terms_by_document_frequency(index, phrase_terms)

    matching_pages = None

    for term in filter_terms:
        term_entry = index.get(term, {})

        if not term_entry:
            return []

        pages_for_term = set(term_entry.keys())

        if matching_pages is None:
            matching_pages = pages_for_term
        else:
            matching_pages = matching_pages.intersection(pages_for_term)

    if not matching_pages:
        return []

    results = []

    for page_url in matching_pages:
        position_lists = [
            index[term][page_url]["positions"]
            for term in phrase_terms
        ]

        phrase_positions = _find_consecutive_phrase_positions(position_lists)

        if phrase_positions:
            results.append(
                {
                    "url": page_url,
                    "phrase": " ".join(phrase_terms),
                    "phrase_positions": phrase_positions,
                    "match_count": len(phrase_positions),
                }
            )

    return sorted(
        results,
        key=lambda result: (-result["match_count"], result["url"]),
    )

#checks for spelling errors
def suggest_terms(
    index: Dict[str, Any],
    query: str,
    max_suggestions: int = 3,
    cutoff: float = 0.7,
) -> Dict[str, List[str]]:
    query_terms = list(dict.fromkeys(tokenise(query)))
    vocabulary = list(index.keys())
    suggestions = {}

    for term in query_terms:
        if term in index:
            continue

        close_matches = get_close_matches(
            term,
            vocabulary,
            n=max_suggestions,
            cutoff=cutoff,
        )

        if close_matches:
            suggestions[term] = close_matches

    return suggestions

#orders query terms based on how common they are to improve efficiency of multi-word search
def order_terms_by_document_frequency(index: Dict[str, Any], terms: List[str]) -> List[str]:
    return sorted(terms, key=lambda term: len(index.get(term, {})))