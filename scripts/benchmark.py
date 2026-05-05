import statistics
import time
from pathlib import Path
from typing import Any, Callable, Dict, List
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.indexer import build_inverted_index
from src.search import find_pages_ranked, phrase_search, suggest_terms


def generate_synthetic_records(
    page_count: int,
    quotes_per_page: int,
    words_per_quote: int,
    vocabulary_size: int,
) -> List[Dict[str, Any]]:
    """
    Generate predictable synthetic quote records for benchmarking.

    This avoids repeatedly crawling the live website and makes the benchmark
    repeatable.
    """
    records = []

    for page_number in range(page_count):
        url = f"page{page_number}"

        for quote_number in range(quotes_per_page):
            words = [
                f"term{(page_number + quote_number + word_number) % vocabulary_size}"
                for word_number in range(words_per_quote)
            ]

            records.append(
                {
                    "url": url,
                    "quote": " ".join(words),
                    "author": f"Author {page_number}",
                    "tags": ["benchmark", f"tag{page_number % 5}"],
                }
            )

    return records


def time_operation(operation: Callable[[], Any], repeats: int = 5) -> float:
    """
    Return the mean runtime of an operation in seconds.
    """
    timings = []

    for _ in range(repeats):
        start_time = time.perf_counter()
        operation()
        end_time = time.perf_counter()
        timings.append(end_time - start_time)

    return statistics.mean(timings)


def run_benchmark() -> str:
    """
    Run indexing and search benchmarks and return a Markdown report.
    """
    benchmark_cases = [
        {
            "name": "Small",
            "page_count": 10,
            "quotes_per_page": 5,
            "words_per_quote": 10,
            "vocabulary_size": 50,
        },
        {
            "name": "Medium",
            "page_count": 50,
            "quotes_per_page": 10,
            "words_per_quote": 15,
            "vocabulary_size": 250,
        },
        {
            "name": "Large",
            "page_count": 100,
            "quotes_per_page": 20,
            "words_per_quote": 20,
            "vocabulary_size": 500,
        },
    ]

    lines = [
        "# Benchmark Results",
        "",
        "Benchmarks were run using synthetic records so results are repeatable and do not depend on network speed.",
        "",
        "| Dataset | Records | Build index time (s) | Ranked search time (s) | Phrase search time (s) | Suggestion time (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for case in benchmark_cases:
        records = generate_synthetic_records(
            page_count=case["page_count"],
            quotes_per_page=case["quotes_per_page"],
            words_per_quote=case["words_per_quote"],
            vocabulary_size=case["vocabulary_size"],
        )

        build_time = time_operation(lambda: build_inverted_index(records), repeats=3)
        index = build_inverted_index(records)

        ranked_search_time = time_operation(
            lambda: find_pages_ranked(index, "term1 term2"),
            repeats=10,
        )

        phrase_search_time = time_operation(
            lambda: phrase_search(index, "term1 term2"),
            repeats=10,
        )

        suggestion_time = time_operation(
            lambda: suggest_terms(index, "trm1"),
            repeats=10,
        )

        lines.append(
            f"| {case['name']} | {len(records)} | "
            f"{build_time:.6f} | {ranked_search_time:.6f} | "
            f"{phrase_search_time:.6f} | {suggestion_time:.6f} |"
        )

    return "\n".join(lines)


def main() -> None:
    report = run_benchmark()

    output_path = Path("docs/BENCHMARK_RESULTS.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nBenchmark report written to {output_path}")


if __name__ == "__main__":
    main()