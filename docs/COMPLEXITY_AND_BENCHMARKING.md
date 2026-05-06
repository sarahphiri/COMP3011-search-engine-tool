# Complexity Analysis and Benchmarking

This document summarises the main algorithmic choices in the search engine tool, their expected complexity, and the benchmarking approach used to evaluate performance.

## Complexity Notation

| Symbol | Meaning |
|---|---|
| `P` | Number of crawled pages |
| `R` | Number of quote records |
| `T` | Total number of tokens indexed |
| `V` | Number of unique terms in the vocabulary |
| `D` | Number of indexed pages/documents |
| `Q` | Number of query terms |
| `df(t)` | Number of pages containing term `t` |
| `K` | Number of candidate pages after filtering |
| `L` | Number of terms in a phrase query |

## Crawler Complexity

The crawler visits each page once and parses the quote blocks on that page.

Expected complexity:

```text
O(P + total HTML parsed)
```

In practice, the runtime is intentionally affected by the required politeness delay. Since the crawler waits at least six seconds between successive requests, the crawl time is dominated by:

```text
6 × (P - 1) seconds
```

This is not an inefficiency in the implementation. It is a requirement designed to avoid sending requests too aggressively to the website.

## Index Construction Complexity

The indexer tokenises each crawled record and inserts each token into the inverted index.

Expected time complexity:

```text
O(T)
```

Each token is processed once. Dictionary lookup and insertion are average-case `O(1)` operations.

Expected space complexity:

```text
O(T)
```

The index stores word occurrences through frequency counts and position lists.

## Inverted Index Design

The index uses the following nested dictionary structure:

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

This avoids scanning every page during search. Instead, the tool directly retrieves the posting list for each query term.

This is more efficient than a brute-force search approach, where every page would need to be scanned for every query.

## Print Command Complexity

The `print <word>` command performs a dictionary lookup for the requested word.

Expected lookup complexity:

```text
O(1)
```

Displaying the result depends on how many pages contain that word:

```text
O(df(t))
```

where `df(t)` is the number of pages containing the term.

## Multi-Word Search Complexity

For a multi-word query, the search retrieves the posting list for each query term and intersects the corresponding page sets.

Expected complexity:

```text
O(sum(df(t)) for each query term)
```

The implementation improves this by ordering query terms by document frequency before performing intersections. This means rarer terms are processed first, which reduces the candidate page set earlier.

For example, in a query such as:

```text
find life inspiration
```

if `inspiration` appears on fewer pages than `life`, the search begins with `inspiration` first. This reduces the number of candidate pages that need to be checked against the remaining terms.

## TF-IDF Ranking Complexity

TF-IDF ranking scores only the pages that contain the required query terms.

Expected complexity:

```text
O(Q × K)
```

where:

- `Q` is the number of query terms
- `K` is the number of candidate pages after filtering

This is more efficient than scoring every indexed page for every query because the tool only ranks pages that already match the query terms.

## Phrase Search Complexity

Phrase search uses the stored word positions in the inverted index.

The search first finds pages containing all phrase terms, then checks whether their positions are consecutive.

Expected complexity:

```text
O(sum(df(t)) + K × position checks)
```

The position lists allow exact phrase matching without scanning raw page text again.

For example, for the phrase:

```text
"good friends"
```

the tool checks whether the position of `friends` is exactly one position after the position of `good` on the same page.

## Query Suggestion Complexity

Query suggestions compare missing query terms against the indexed vocabulary.

Expected complexity:

```text
O(V)
```

where `V` is the number of unique indexed terms.

This is acceptable for this coursework dataset because the vocabulary is relatively small. The number of suggestions is also limited so the output remains concise.

## Benchmarking Approach

The benchmark script uses synthetic records rather than live crawling. This makes the benchmark repeatable and avoids network speed or the required crawler politeness delay affecting the results.

The benchmark measures:

- index construction time
- TF-IDF ranked search time
- phrase search time
- query suggestion time

The benchmark script is located at:

```text
scripts/benchmark.py
```

It can be run using:

```bash
python scripts/benchmark.py
```

The results are written to:

```text
docs/BENCHMARK_RESULTS.md
```

## Why Synthetic Data Is Used

Synthetic data is used for benchmarking because it allows the same test conditions to be repeated. Live crawling would make benchmark results less reliable because runtime would depend on network speed, website response time, and the required six-second politeness delay.

Using synthetic records means the benchmark focuses on the performance of the indexing and search algorithms themselves.

## Summary of Main Operations

| Operation | Expected Complexity | Notes |
|---|---:|---|
| Crawling | `O(P + total HTML parsed)` | Runtime is dominated by the required six-second politeness delay |
| Index construction | `O(T)` | Each token is processed once |
| `print <word>` lookup | `O(1)` average lookup, `O(df(t))` to display | Uses direct dictionary lookup |
| Multi-word search | `O(sum(df(t)))` | Posting lists are intersected |
| Optimised multi-word search | `O(sum(df(t)))`, but reduced in practice | Rarer query terms are processed first |
| TF-IDF ranking | `O(Q × K)` | Only candidate pages are scored |
| Phrase search | `O(sum(df(t)) + K × position checks)` | Uses stored word positions |
| Query suggestions | `O(V)` | Compares missing terms against vocabulary |

## Optimisation Summary

The main optimisation is the use of an inverted index rather than scanning all page text during every search.

Additional optimisation is provided by ordering query terms by document frequency before intersecting posting lists. This means rarer terms are processed first, which reduces the candidate page set earlier.

TF-IDF ranking and phrase search are then applied only to candidate pages, keeping query processing focused and efficient.

## Reflection on Performance

The dataset used in this coursework is relatively small, so most search operations are very fast in practice. However, the implementation choices are still important because they show how the tool could scale more effectively than a brute-force approach.

The inverted index, document-frequency ordering, TF-IDF ranking, and phrase search all demonstrate that the tool uses search-engine-style data structures and algorithms rather than simply scanning strings directly.