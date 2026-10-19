from __future__ import annotations

import csv
import random
import time
from pathlib import Path

from fm_index import FMIndex
from wavelet_tree import WaveletTree


SEED = 20260724
ALPHABET = ["$", "a", "c", "g"]
TEXT_CHARACTERS = ["a", "c", "g"]


def direct_rank(text: str, char: str, position: int) -> int:
    return text[:position].count(char)


def direct_select(text: str, char: str, occurrence: int) -> int:
    positions = [
        index
        for index, value in enumerate(text, start=1)
        if value == char
    ]

    if occurrence < 1 or occurrence > len(positions):
        raise IndexError("The requested occurrence does not exist.")

    return positions[occurrence - 1]


def direct_count(text: str, pattern: str) -> int:
    if pattern == "":
        return len(text)

    last_start = len(text) - len(pattern)

    if last_start < 0:
        return 0

    return sum(
        text.startswith(pattern, position)
        for position in range(last_start + 1)
    )


def random_text(length: int) -> str:
    if length < 1:
        raise ValueError("The length must be positive.")

    body = "".join(
        random.choice(TEXT_CHARACTERS)
        for _ in range(length - 1)
    )

    return body + "$"


def test_wavelet_tree(text: str) -> None:
    tree = WaveletTree(text, ALPHABET)

    for position in range(1, len(text) + 1):
        assert tree.access(position) == text[position - 1]

    for char in ALPHABET:
        for position in range(0, len(text) + 1):
            assert (
                tree.rank(char, position)
                == direct_rank(text, char, position)
            )

        frequency = text.count(char)

        for occurrence in range(1, frequency + 1):
            assert (
                tree.select(char, occurrence)
                == direct_select(text, char, occurrence)
            )


def test_fm_index(text: str, pattern_count: int = 100) -> None:
    index = FMIndex(text)

    for _ in range(pattern_count):
        length = random.randint(1, 6)
        pattern = "".join(
            random.choice(TEXT_CHARACTERS)
            for _ in range(length)
        )

        assert index.count(pattern) == direct_count(text, pattern)


def run_correctness_tests() -> None:
    running_example = "acagcagg$"

    test_wavelet_tree(running_example)
    test_fm_index(running_example)

    for _ in range(50):
        length = random.randint(10, 80)
        text = random_text(length)

        test_wavelet_tree(text)
        test_fm_index(text, pattern_count=50)

    print("All correctness tests passed.")


def time_average(function, arguments: list[tuple]) -> float:
    start = time.perf_counter()

    for argument in arguments:
        function(*argument)

    elapsed = time.perf_counter() - start
    return elapsed / len(arguments)


def benchmark_wavelet_tree(results_directory: Path) -> None:
    sizes = [1000, 5000, 10000, 50000, 100000]
    query_count = 10000
    rows: list[dict[str, float | int]] = []

    for size in sizes:
        text = random_text(size)

        start = time.perf_counter()
        tree = WaveletTree(text, ALPHABET)
        construction_time = time.perf_counter() - start

        access_queries = [
            (random.randint(1, size),)
            for _ in range(query_count)
        ]

        rank_queries = [
            (
                random.choice(TEXT_CHARACTERS),
                random.randint(0, size),
            )
            for _ in range(query_count)
        ]

        select_queries: list[tuple[str, int]] = []

        for _ in range(query_count):
            char = random.choice(TEXT_CHARACTERS)
            frequency = text.count(char)
            occurrence = random.randint(1, frequency)
            select_queries.append((char, occurrence))

        access_time = time_average(
            tree.access,
            access_queries,
        )

        rank_time = time_average(
            tree.rank,
            rank_queries,
        )

        select_time = time_average(
            tree.select,
            select_queries,
        )

        row = {
            "n": size,
            "construction_seconds": construction_time,
            "access_microseconds": access_time * 1_000_000,
            "rank_microseconds": rank_time * 1_000_000,
            "select_microseconds": select_time * 1_000_000,
        }

        rows.append(row)

        print(
            f"Wavelet tree n={size}: "
            f"build={construction_time:.6f}s, "
            f"access={row['access_microseconds']:.3f}us, "
            f"rank={row['rank_microseconds']:.3f}us, "
            f"select={row['select_microseconds']:.3f}us"
        )

    output = results_directory / "wavelet_performance.csv"

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def benchmark_fm_index(results_directory: Path) -> None:
    sizes = [500, 1000, 2000, 4000]
    query_count = 500
    pattern_length = 6
    rows: list[dict[str, float | int]] = []

    for size in sizes:
        text = random_text(size)

        start = time.perf_counter()
        index = FMIndex(text)
        construction_time = time.perf_counter() - start

        patterns = [
            "".join(
                random.choice(TEXT_CHARACTERS)
                for _ in range(pattern_length)
            )
            for _ in range(query_count)
        ]

        fm_arguments = [(pattern,) for pattern in patterns]
        direct_arguments = [
            (text, pattern)
            for pattern in patterns
        ]

        fm_time = time_average(
            index.count,
            fm_arguments,
        )

        direct_time = time_average(
            direct_count,
            direct_arguments,
        )

        for pattern in patterns:
            assert index.count(pattern) == direct_count(text, pattern)

        row = {
            "n": size,
            "construction_seconds": construction_time,
            "fm_query_microseconds": fm_time * 1_000_000,
            "direct_query_microseconds": direct_time * 1_000_000,
        }

        rows.append(row)

        print(
            f"FM index n={size}: "
            f"build={construction_time:.6f}s, "
            f"FM query={row['fm_query_microseconds']:.3f}us, "
            f"direct query={row['direct_query_microseconds']:.3f}us"
        )

    output = results_directory / "fm_index_performance.csv"

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    random.seed(SEED)

    results_directory = Path("results")
    results_directory.mkdir(parents=True, exist_ok=True)

    run_correctness_tests()
    benchmark_wavelet_tree(results_directory)
    benchmark_fm_index(results_directory)

    print("Experiment files were written to the results directory.")


if __name__ == "__main__":
    main()