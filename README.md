# COMP3011 Search Engine Tool

A command-line search engine built for the COMP3011 coursework. The tool crawls [`quotes.toscrape.com`](https://quotes.toscrape.com/), extracts quote data, builds an inverted index, saves and loads the index from file, and allows users to search the indexed content through a terminal interface.

The project implements the required `build`, `load`, `print`, and `find` commands, alongside additional search features such as TF-IDF ranking, phrase search, query suggestions, benchmarking, automated testing, and GitHub Actions.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [How the Search Engine Works](#how-the-search-engine-works)
- [Design Decisions](#design-decisions)
- [Testing](#testing)
- [Version Control Workflow](#version-control-workflow)
- [Generative AI Use](#generative-ai-use)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project is a small search engine that works from the command line. It performs four main tasks:

1. Crawls pages from `quotes.toscrape.com`
2. Extracts quote text, authors, tags, and page URLs
3. Builds an inverted index containing word frequencies and positions
4. Lets the user search the saved index through CLI commands

The core data structure is an inverted index implemented using nested Python dictionaries.

```text
word → page URL → frequency and positions
```

This allows the tool to look up matching pages efficiently without scanning all quote text for every query.

---

## Features

### Required Features

- Crawl `quotes.toscrape.com`
- Follow pagination links
- Apply a six-second delay between successive requests
- Extract quote text, authors, tags, and URLs
- Build an inverted index
- Store word frequency and word positions
- Save the index to the file system
- Load the saved index from file
- Provide a command-line interface
- Support the required commands:
  - `build`
  - `load`
  - `print <word>`
  - `find <query>`

### Additional Features

- Multi-word search
- TF-IDF ranked search results
- Exact phrase search using stored word positions
- Query suggestions for misspelled terms
- Help command showing available commands
- Edge-case handling for empty input and missing words
- Complexity analysis documentation
- Benchmark script and benchmark results
- Professional pytest test suite
- Mocked crawler and CLI tests
- Automated GitHub Actions testing pipeline
- 80 passing tests
- 93% total test coverage

---

## Project Structure

```text
COMP3011-search-engine-tool/

├── data/
│   └── index.json
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── main.py
│   └── search.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── README.md
└── requirements.txt
```

### Main Files

| File | Purpose |
|---|---|
| `src/crawler.py` | Fetches pages, parses HTML, extracts quote data, and follows pagination |
| `src/indexer.py` | Tokenises text and builds the inverted index |
| `src/search.py` | Saves/loads the index and handles search, ranking, phrase search, and suggestions |
| `src/main.py` | Provides the command-line interface |
| `tests/` | Contains unit tests and mocked integration-style tests |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sarahphiri/COMP3011-search-engine-tool.git
cd COMP3011-search-engine-tool
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

Run the command-line tool with:

```bash
python -m src.main
```

You should then see the interactive search prompt.

```text
COMP3011 Search Engine Tool

Available commands:
  build
  load
  print <word>
  find <query>
  find "<phrase>"
  phrase <query>
  suggest <query>
  help
  exit
```

---

## Command Reference

### `help`

Shows the available commands.

```text
help
```

### `build`

Crawls the website, extracts quote records, builds the inverted index, and saves it to `data/index.json`.

```text
build
```

The crawler includes the required six-second delay between successive requests. Because of this delay, the build command may take over a minute to complete.

### `load`

Loads the saved index from `data/index.json`.

```text
load
```

### `print <word>`

Prints the inverted index entry for a single word.

```text
print life
```

Example output structure:

```text
{
  "https://quotes.toscrape.com/page/1/": {
    "frequency": 1,
    "positions": [12]
  }
}
```

### `find <query>`

Finds pages containing the query term or terms.

```text
find life
```

Multi-word search is also supported:

```text
find good friends
```

The tool returns pages containing all query terms and ranks them using TF-IDF.

### `find "<phrase>"`

Finds exact phrase matches using word positions.

```text
find "good friends"
```

### `phrase <query>`

Alternative command for exact phrase search.

```text
phrase good friends
```

### `suggest <query>`

Suggests close indexed terms for misspelled queries.

```text
suggest frend
```

Example:

```text
Suggestions for: 'frend'
- frend: friend
```

### `exit`

Exits the program.

```text
exit
```

---

## Example Demo Flow

The following commands demonstrate the main required and additional functionality:

```text
help
build
load
print life
find life
find good friends
phrase good friends
suggest frend
print nonsenseword
find
exit
```

This demonstrates:

- all required commands from the coursework brief
- multi-word search
- TF-IDF ranking
- advanced phrase search
- query suggestions
- edge-case handling for missing words and empty queries

---

## How the Search Engine Works

### 1. Crawling

The crawler starts at:

```text
https://quotes.toscrape.com/
```

It fetches the page HTML, extracts quote blocks, and follows the `next` pagination link until there are no more pages.

The crawler extracts:

- quote text
- author
- tags
- page URL

The crawler also includes a six-second delay before making another request.

### 2. Tokenisation

The tokeniser converts text into lowercase searchable terms.

```python
re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())
```

This makes search case-insensitive and removes most punctuation while preserving useful tokens such as words, numbers, and apostrophes.

### 3. Inverted Index Construction

The inverted index is implemented as nested dictionaries.

```text
word → page URL → frequency and positions
```

Example:

```json
{
  "life": {
    "https://quotes.toscrape.com/page/1/": {
      "frequency": 2,
      "positions": [4, 18]
    }
  }
}
```

For each token, the index stores:

| Field | Purpose |
|---|---|
| `frequency` | Counts how often the word appears on a page |
| `positions` | Stores word positions for phrase search |

### 4. Search

For a single-word query, the tool looks up the word directly in the index.

For a multi-word query, the tool finds pages containing all query terms by intersecting the matching page sets.

### 5. Ranking

Search results are ranked using TF-IDF.

```text
score = term frequency × inverse document frequency
```

This means a page scores higher when:

- the query term appears more often on that page
- the query term is less common across the collection

### 6. Phrase Search

Phrase search uses the stored word positions.

For example, the phrase:

```text
good friends
```

matches only when:

```text
good position + 1 = friends position
```

This allows the tool to distinguish between pages that contain both words separately and pages where the phrase appears exactly.

### 7. Query Suggestions

Query suggestions use close matching against the indexed vocabulary. This allows the tool to suggest likely intended terms when the user enters a misspelled query.

---

## Design Decisions

### Inverted Index

I used an inverted index because it is the standard data structure for efficient text search. Instead of scanning every quote for every query, the system can directly look up the pages associated with a word.

### Nested Dictionaries

The inverted index is implemented using nested Python dictionaries because dictionaries provide fast average-case lookup.

```text
word → page URL → frequency and positions
```

This makes the structure simple, readable, and efficient for the dataset size.

### Frequency and Positions

The index stores both frequency and positions.

Frequency is used for TF-IDF ranking. Positions are used for exact phrase search.

This makes the index more useful than a simple word-to-page mapping.

### Page Position Offsets

The indexer uses `page_position_offsets` to keep word positions continuous across multiple quote records on the same page.

A small gap is added between records on the same page. This prevents phrase search from accidentally matching the end of one quote with the beginning of another separate quote.

### JSON Storage

The index is saved as JSON.

The tradeoff is that JSON is not as scalable as a database for very large indexes. However, for this coursework dataset, JSON is appropriate because it is:

- simple
- readable
- easy to inspect
- easy to load and save
- suitable for the dataset size

### TF-IDF Ranking

TF-IDF ranking was added to make the search results more meaningful. Instead of returning raw matches only, the tool scores pages based on term frequency and document frequency.

### Rarest-Term-First Query Processing

For multi-word queries, query terms are ordered by document frequency before intersecting page sets.

This means rarer terms are processed first, reducing the candidate page set earlier and improving search efficiency in practice.

### Phrase Search

Phrase search was added as an advanced query-processing feature. It uses stored word positions to check whether words appear consecutively and in the correct order.

### Query Suggestions

Query suggestions improve usability by helping users recover from misspellings.

The tradeoff is that close matching compares against the indexed vocabulary, which is acceptable for this dataset but would need a more scalable method for a much larger search engine.

---

## Research-Informed Search Design

The implementation was informed by research into common search engine techniques, including:

- inverted indexes
- tokenisation and normalisation
- posting lists
- term frequency
- inverse document frequency
- TF-IDF ranking
- phrase search using word positions
- query suggestion techniques

These concepts helped shape the design of the tool and made the implementation closer to a real search-engine workflow than a simple string-matching program.

---

## Testing

The project uses `pytest` for testing.

Run the full test suite with:

```bash
python -m pytest
```

Run the test suite with coverage:

```bash
python -m pytest --cov=src --cov-report=term-missing tests/
```

Current test status:

```text
80 tests passed
93% total coverage
```

### Test Coverage by Area

| Area | Tested |
|---|---|
| Crawler parsing | Yes |
| Crawler pagination | Yes |
| Network error handling | Yes |
| Mocked crawler requests | Yes |
| Required crawler delay behaviour | Yes |
| Tokenisation | Yes |
| Normalisation | Yes |
| Inverted index construction | Yes |
| Frequency counting | Yes |
| Position tracking | Yes |
| Save/load index | Yes |
| Missing index file handling | Yes |
| Single-word search | Yes |
| Multi-word search | Yes |
| TF-IDF ranking | Yes |
| Phrase search | Yes |
| Query suggestions | Yes |
| CLI command handling | Yes |
| Empty and invalid input | Yes |

### Mocking Strategy

The test suite uses mocking to avoid unreliable or slow tests.

Crawler tests use mocked HTML rather than relying on the live website. This makes the tests repeatable and independent of network conditions.

The crawler delay is also mocked so that the six-second politeness delay can be tested without slowing down the test suite.

CLI tests mock user input so that commands such as `build`, `load`, `print`, `find`, `phrase`, and `suggest` can be tested automatically.

---

### Complexity Summary

| Operation | Expected Complexity | Notes |
|---|---:|---|
| Crawling | `O(P + total HTML parsed)` | Runtime is dominated by the required delay |
| Index construction | `O(T)` | Each token is processed once |
| Word lookup | `O(1)` average lookup | Uses dictionary access |
| Multi-word search | `O(sum(df(t)))` | Intersects posting lists |
| TF-IDF ranking | `O(Q × K)` | Scores candidate pages only |
| Phrase search | `O(sum(df(t)) + K × position checks)` | Uses stored word positions |
| Query suggestions | `O(V)` | Compares against indexed vocabulary |

Where:

- `P` is the number of pages
- `T` is the number of tokens
- `df(t)` is the number of pages containing term `t`
- `Q` is the number of query terms
- `K` is the number of candidate pages
- `V` is the vocabulary size

---

## Version Control Workflow

The project was developed using GitHub with a structured workflow.

### Commit Style

Commits use clear prefixes to make the history easier to follow.

Examples:

| Prefix | Meaning |
|---|---|
| `feat:` | New feature |
| `test:` | Test changes |
| `docs:` | Documentation changes |
| `fix:` | Bug fix |
| `chore:` | Setup or maintenance work |
| `ci:` | Continuous integration changes |
| `perf:` | Performance or optimisation changes |

### Branching and Pull Requests

Features were developed on separate branches and merged through pull requests.

This made each feature easier to review before it reached `main`.

### Issues, Milestones, and Project Board

The work was organised using GitHub issues, milestones, and a project board.

Milestones grouped related tasks, such as:

- crawler
- indexing
- storage and CLI commands
- testing
- advanced search features
- documentation
- final submission

The project board tracked work through:

```text
Todo → In Progress → Testing → Done
```

This helped ensure features were not treated as complete until they had been tested and merged.

---

## Generative AI Use

Generative AI, specifically ChatGPT, was used throughout this project as a development support tool. It was used to support the development process, but not as a replacement for understanding, testing, or decision-making.

### How GenAI Was Used

GenAI was used for:

- planning the project structure and development workflow
- breaking the coursework requirements into smaller implementation tasks
- generating initial code for the crawler, indexer, search logic, and CLI
- debugging errors, such as import issues, indentation problems, and failing tests
- improving the implementation of the inverted index
- understanding and applying search engine concepts such as:
  - inverted indexes
  - tokenisation
  - posting lists
  - TF-IDF ranking
  - phrase search
  - query suggestions
  - document frequency optimisation
- suggesting edge cases for testing
- helping create pytest tests and mocked tests
- supporting GitHub workflow decisions, including issues, milestones, branches, pull requests, and commit messages
- helping design the GitHub Actions automated testing pipeline
- improving documentation, including the README, complexity analysis, and benchmarking explanation
- helping prepare and refine the video script

### Critical Evaluation

GenAI was especially useful because it made development more efficient and allowed me to ask specific questions when I was stuck. It also helped me learn more about search algorithms and testing strategies by explaining concepts in a practical way.

However, I used GenAI through a back-and-forth process instead of accepting its output automatically. I reviewed suggestions, tested the code, corrected errors, and checked that the implementation matched the coursework brief. Although ChatGPT was effective for generating code, the final design decisions were reviewed by me.

One limitation was that GenAI could sometimes drift away from the requirements. For example, it occasionally suggested repository structures or features that were more complex than needed for this coursework. This caused delays because I had to realign the work with the brief and make sure the final project stayed focused on the required search engine functionality.

To use GenAI responsibly, I commented and reviewed the code myself afterwards so that I understood what each part was doing. I also validated the implementation using manual testing, automated tests, and coverage checks.

Overall, GenAI was helpful as an assistant because it improved efficiency and supported learning. Its responsible use relied on critical review, testing, and personal motivation to check that the generated output was correct, ethical, and appropriate for the task.

---

## Limitations

This project is designed for a small coursework dataset, so some implementation choices prioritise clarity and suitability over large-scale production performance.

Current limitations include:

- The crawler is designed specifically for `quotes.toscrape.com`
- JSON storage is suitable for this dataset but not ideal for very large indexes
- Query suggestions compare against the full vocabulary, which may not scale efficiently
- The tool does not include a graphical interface
- The search engine indexes quote text, authors, and tags, but does not currently support filtering by author or tag as separate fields

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Run tests using:

```bash
python -m pytest
```

### No index file found

Run:

```text
build
```

inside the CLI before using:

```text
load
```

The `build` command creates:

```text
data/index.json
```

### Build command takes time

This is expected. The crawler includes a six-second delay between successive requests to meet the politeness requirement.

### Coverage command not working

Install the coverage dependency:

```bash
pip install pytest-cov
```

Then run:

```bash
python -m pytest --cov=src --cov-report=term-missing tests/
```

---

## Coursework Requirement Coverage

| Requirement | Implemented |
|---|---|
| Crawl `quotes.toscrape.com` | Yes |
| Use BeautifulSoup | Yes |
| Include delay between requests | Yes |
| Build inverted index | Yes |
| Store frequency and positions | Yes |
| Save index to file | Yes |
| Load index from file | Yes |
| `build` command | Yes |
| `load` command | Yes |
| `print <word>` command | Yes |
| `find <query>` command | Yes |
| Multi-word queries | Yes |
| Edge-case handling | Yes |
| Testing | Yes |
| Mocking | Yes |
| Automated testing pipeline | Yes |
| Version control workflow | Yes |
| GenAI reflection | Yes |
| Advanced search features | Yes |
| Complexity and benchmarking | Yes |

---

## Summary

This project implements a complete command-line search engine with:

- crawling
- parsing
- inverted indexing
- file-based storage
- search
- TF-IDF ranking
- phrase search
- query suggestions
- edge-case handling
- professional testing
- automated CI
- benchmarking
- documented design decisions
- structured version control
- GenAI critical evaluation

The implementation is intentionally simple enough to be understandable, but includes core search-engine concepts such as inverted indexes, posting lists, frequency counts, word positions, TF-IDF ranking, phrase matching, and query optimisation.