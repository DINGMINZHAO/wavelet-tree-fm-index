from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIRECTORY = Path("results")
FIGURES_DIRECTORY = Path("figures")


def read_csv(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            {
                key: float(value)
                for key, value in row.items()
            }
            for row in reader
        ]


def plot_wavelet_construction(
    rows: list[dict[str, float]],
) -> None:
    sizes = [row["n"] for row in rows]
    times = [
        row["construction_seconds"] * 1000
        for row in rows
    ]

    plt.figure(figsize=(6.5, 4.2))
    plt.plot(sizes, times, marker="o")
    plt.xlabel("Text length n")
    plt.ylabel("Construction time in milliseconds")
    plt.title("Wavelet Tree Construction Time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "wavelet_construction_time.pdf",
        bbox_inches="tight",
    )
    plt.close()


def plot_wavelet_queries(
    rows: list[dict[str, float]],
) -> None:
    sizes = [row["n"] for row in rows]

    plt.figure(figsize=(6.5, 4.2))
    plt.plot(
        sizes,
        [row["access_microseconds"] for row in rows],
        marker="o",
        label="Access",
    )
    plt.plot(
        sizes,
        [row["rank_microseconds"] for row in rows],
        marker="s",
        label="Rank",
    )
    plt.plot(
        sizes,
        [row["select_microseconds"] for row in rows],
        marker="^",
        label="Select",
    )

    plt.xlabel("Text length n")
    plt.ylabel("Average query time in microseconds")
    plt.title("Wavelet Tree Query Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "wavelet_query_time.pdf",
        bbox_inches="tight",
    )
    plt.close()


def plot_fm_queries(
    rows: list[dict[str, float]],
) -> None:
    sizes = [row["n"] for row in rows]

    plt.figure(figsize=(6.5, 4.2))
    plt.plot(
        sizes,
        [row["fm_query_microseconds"] for row in rows],
        marker="o",
        label="FM index",
    )
    plt.plot(
        sizes,
        [row["direct_query_microseconds"] for row in rows],
        marker="s",
        label="Direct scanning",
    )

    plt.xlabel("Text length n")
    plt.ylabel("Average query time in microseconds")
    plt.title("Pattern Counting Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIRECTORY / "fm_query_time.pdf",
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    FIGURES_DIRECTORY.mkdir(parents=True, exist_ok=True)

    wavelet_rows = read_csv(
        RESULTS_DIRECTORY / "wavelet_performance.csv"
    )
    fm_rows = read_csv(
        RESULTS_DIRECTORY / "fm_index_performance.csv"
    )

    plot_wavelet_construction(wavelet_rows)
    plot_wavelet_queries(wavelet_rows)
    plot_fm_queries(fm_rows)

    print("All figures were written to the figures directory.")


if __name__ == "__main__":
    main()