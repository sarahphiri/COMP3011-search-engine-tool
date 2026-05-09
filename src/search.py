import json
from difflib import get_close_matches
from math import log
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

from src.indexer import tokenise


DEFAULT_INDEX_PATH = Path("data/index.json")
DEFAULT_RECORDS_PATH = Path("data/records.json")


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
    
def save_records(
    records: List[Dict[str, Any]],
    file_path: Path = DEFAULT_RECORDS_PATH,
) -> None:
    """
    Save crawled quote records to the file system as JSON.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def load_records(file_path: Path = DEFAULT_RECORDS_PATH) -> List[Dict[str, Any]]:
    """
    Load previously saved quote records from the file system.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"No quote records file found at {file_path}. Run the build command first."
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

def is_quoted_phrase(query: str) -> bool:
    """
    Return True if a query is wrapped in double quotation marks.
    """
    stripped_query = query.strip()

    return (
        len(stripped_query) >= 2
        and stripped_query[0] == '"'
        and stripped_query[-1] == '"'
    )


def strip_query_quotes(query: str) -> str:
    """
    Remove surrounding double quotation marks from a query.
    """
    return query.strip()[1:-1].strip()


def _find_consecutive_phrase_positions(position_lists: List[List[int]]) -> List[int]:
    """
    Return starting positions where all term positions appear consecutively.

    Example:
    good positions = [3, 10]
    friends positions = [4]
    phrase starts at [3]
    """
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


def phrase_search(index: Dict[str, Any], phrase: str) -> List[Dict[str, Any]]:
    """
    Find pages where the query terms appear consecutively.

    This uses word positions stored in the inverted index.

    The function uses document-frequency ordering only to reduce the candidate
    page set efficiently. It keeps the original phrase term order when checking
    positions, because phrase matching depends on word order.
    """
    phrase_terms = tokenise(phrase)

    if not phrase_terms:
        return []

    # Use rarest terms first only for filtering candidate pages.
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
        # Important: use the original phrase_terms order here.
        # This is what checks whether the phrase appears in the correct order.
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


def suggest_terms(
    index: Dict[str, Any],
    query: str,
    max_suggestions: int = 3,
    cutoff: float = 0.7,
) -> Dict[str, List[str]]:
    """
    Suggest close indexed terms for query terms that are not in the index.

    This is useful when the user misspells a word or searches for a term
    that does not exist in the current index.
    """
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

def order_terms_by_document_frequency(index: Dict[str, Any], terms: List[str]) -> List[str]:
    """
    Order query terms from rarest to most common based on document frequency.

    This improves multi-word search because intersections start with the
    smallest posting lists first.
    """
    return sorted(terms, key=lambda term: len(index.get(term, {})))

def _normalise_tags(record: Dict[str, Any]) -> List[str]:
    """
    Return record tags as lowercase strings.
    """
    return [str(tag).lower() for tag in record.get("tags", [])]


def _record_vocabulary(record: Dict[str, Any]) -> List[str]:
    """
    Build a list of searchable terms from a quote record.
    """
    quote_terms = tokenise(str(record.get("quote", "")))
    author_terms = tokenise(str(record.get("author", "")))
    tag_terms = []

    for tag in record.get("tags", []):
        tag_terms.extend(tokenise(str(tag)))

    return list(dict.fromkeys(quote_terms + author_terms + tag_terms))


def score_quote_record(record: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Score a quote record against a discovery query.

    The scoring is explainable:
    - quote text matches are rewarded
    - tag matches are rewarded more strongly
    - author matches are rewarded
    - exact phrase matches receive a bonus
    - close matches receive a small bonus
    """
    query_terms = list(dict.fromkeys(tokenise(query)))

    if not query_terms:
        return {
            "record": record,
            "score": 0.0,
            "reasons": [],
        }

    quote = str(record.get("quote", ""))
    author = str(record.get("author", ""))
    tags = _normalise_tags(record)

    quote_terms = tokenise(quote)
    author_terms = tokenise(author)
    quote_as_normalised_text = " ".join(quote_terms)

    score = 0.0
    reasons = []

    normalised_query = " ".join(query_terms)

    if len(query_terms) > 1 and normalised_query in quote_as_normalised_text:
        score += 5
        reasons.append("Exact phrase appears in the quote text.")

    for term in query_terms:
        quote_frequency = quote_terms.count(term)

        if quote_frequency > 0:
            score += quote_frequency * 3
            reasons.append(
                f"'{term}' appears in the quote text {quote_frequency} time(s)."
            )

        if term in tags:
            score += 4
            reasons.append(f"'{term}' matches a quote tag.")

        if term in author_terms:
            score += 2
            reasons.append(f"'{term}' appears in the author name.")

        vocabulary = _record_vocabulary(record)
        close_matches = get_close_matches(term, vocabulary, n=2, cutoff=0.8)

        close_matches = [
            match for match in close_matches
            if match != term
        ]

        if close_matches:
            score += 1
            reasons.append(
                f"'{term}' is close to indexed term(s): {', '.join(close_matches)}."
            )

    return {
        "record": record,
        "score": round(score, 4),
        "reasons": reasons,
    }


def discover_quotes(
    records: List[Dict[str, Any]],
    query: str,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Return the top quote-level discovery results for a query.
    """
    if not tokenise(query):
        return []

    scored_results = [
        score_quote_record(record, query)
        for record in records
    ]

    matched_results = [
        result for result in scored_results
        if result["score"] > 0
    ]

    return sorted(
        matched_results,
        key=lambda result: (
            -result["score"],
            str(result["record"].get("author", "")),
            str(result["record"].get("quote", "")),
        ),
    )[:limit]


def lucky_quote(
    records: List[Dict[str, Any]],
    query: str,
) -> Optional[Dict[str, Any]]:
    """
    Return the single best quote discovery result for a query.
    """
    results = discover_quotes(records, query, limit=1)

    if not results:
        return None

    return results[0]