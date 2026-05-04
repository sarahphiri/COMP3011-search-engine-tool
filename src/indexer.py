import re
feature/storage-cli
from typing import Any, Dict, List
from typing import Dict, List, Any
main


def tokenise(text: str) -> List[str]:
    """
feature/storage-cli
    Convert text into lowercase searchable tokens.

    This makes search case-insensitive and removes punctuation.
    Convert text into lowercase word tokens.
    Removes punctuation and ignores empty tokens.
    main
    """
    return re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())


feature/storage-cli
def build_inverted_index(
    records: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Dict[str, Any]]]:
def build_inverted_index(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
 main
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
 feature/storage-cli
    index: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for record in records:
        url = str(record["url"])
    index = {}

    for record in records:
        url = record["url"]
 main

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