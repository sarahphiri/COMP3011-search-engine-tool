#access all necessary imports
import re
from typing import Any, Dict, List

#converts text into tokens
def tokenise(text: str) -> List[str]:
    #this converts to lower case and keeps symbols like apostrophes, numbers, and words
    return re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())

#builds the inverted index (section 1 of the brief) from quote records
def build_inverted_index(
    records: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Dict[str, Any]]]:

    #store the index in this order: word, url, frequency/position
    index: Dict[str, Dict[str, Dict[str, Any]]] = {}
    page_position_offsets: Dict[str, int] = {}

    #loop through every record
    for record in records:
        url = str(record["url"])

        #combine the quote, author, and tags
        combined_text = " ".join(
            [
                str(record.get("quote", "")),
                str(record.get("author", "")),
                " ".join(record.get("tags", [])),
            ]
        )

        #convert the combination into tokens
        tokens = tokenise(combined_text)

        #then skip the records which don't have searchable words
        if not tokens:
            continue

        start_position = page_position_offsets.get(url, 0)

        #loop through the tokens and store its position
        for local_position, token in enumerate(tokens):
            position = start_position + local_position

            #add token to dictionary if its not in index already
            if token not in index:
                index[token] = {}

            #add url if its not in the index already
            if url not in index[token]:
                index[token][url] = {
                    "frequency": 0,
                    "positions": [],
                }

            index[token][url]["frequency"] += 1
            index[token][url]["positions"].append(position)

        page_position_offsets[url] = start_position + len(tokens) + 1

    return index
