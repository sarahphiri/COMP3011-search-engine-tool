import re
from typing import Any, Dict, List


def tokenise(text: str) -> List[str]:
    """
    Convert text into lowercase searchable tokens.

    This makes search case-insensitive and removes punctuation.
    """
    return re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())


def build_inverted_index(
    records: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Build an inverted index from crawled quote records.

    Index structure:
    {
        "word": {
            "url": {
                "frequency": int,
                "positions": [int, int, ...]
            }
        }
    }

    Positions are tracked at page level. A small gap is inserted between
    records from the same page so phrase search does not accidentally match
    across separate quotes.
    """
    index: Dict[str, Dict[str, Dict[str, Any]]] = {}
    page_position_offsets: Dict[str, int] = {}

    for record in records:
        url = str(record["url"])

        combined_text = " ".join(
            [
                str(record.get("quote", "")),
                str(record.get("author", "")),
                " ".join(record.get("tags", [])),
            ]
        )

        tokens = tokenise(combined_text)

        if not tokens:
            continue

        start_position = page_position_offsets.get(url, 0)

        for local_position, token in enumerate(tokens):
            position = start_position + local_position

            if token not in index:
                index[token] = {}

            if url not in index[token]:
                index[token][url] = {
                    "frequency": 0,
                    "positions": [],
                }

            index[token][url]["frequency"] += 1
            index[token][url]["positions"].append(position)

        page_position_offsets[url] = start_position + len(tokens) + 1

    return index

def test_build_index_adds_gap_between_records_on_same_page():
    records = [
        {
            "url": "page1",
            "quote": "good",
            "author": "",
            "tags": [],
        },
        {
            "url": "page1",
            "quote": "friends",
            "author": "",
            "tags": [],
        },
    ]

    index = build_inverted_index(records)

    assert index["good"]["page1"]["positions"] == [0]
    assert index["friends"]["page1"]["positions"] == [2]