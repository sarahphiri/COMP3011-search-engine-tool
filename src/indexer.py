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
    """
    index: Dict[str, Dict[str, Dict[str, Any]]] = {}

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

        for position, token in enumerate(tokens):
            if token not in index:
                index[token] = {}

            if url not in index[token]:
                index[token][url] = {
                    "frequency": 0,
                    "positions": [],
                }

            index[token][url]["frequency"] += 1
            index[token][url]["positions"].append(position)

    return index