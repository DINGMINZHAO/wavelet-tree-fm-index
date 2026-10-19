from __future__ import annotations

from collections import Counter

from wavelet_tree import WaveletTree


class FMIndex:
    """A simplified FM index that supports pattern counting."""

    def __init__(self, text: str) -> None:
        if not text:
            raise ValueError("The text must be nonempty.")

        if text.count("$") != 1:
            raise ValueError("The text must contain exactly one terminator '$'.")

        if not text.endswith("$"):
            raise ValueError("The terminator '$' must appear at the end.")

        self.text = text
        self.length = len(text)
        self.alphabet = sorted(set(text))

        self.suffix_array = self._build_suffix_array(text)
        self.bwt = self._build_bwt(text, self.suffix_array)
        self.cumulative = self._build_cumulative_array(text)

        self.wavelet_tree = WaveletTree(
            self.bwt,
            self.alphabet,
        )

    @staticmethod
    def _build_suffix_array(text: str) -> list[int]:
        """
        Construct the suffix array.

        The returned positions use zero based indexing.
        """
        return sorted(
            range(len(text)),
            key=lambda position: text[position:],
        )

    @staticmethod
    def _build_bwt(
        text: str,
        suffix_array: list[int],
    ) -> str:
        """
        Construct the Burrows Wheeler transform from the suffix array.
        """
        transformed: list[str] = []

        for suffix_start in suffix_array:
            if suffix_start == 0:
                transformed.append(text[-1])
            else:
                transformed.append(text[suffix_start - 1])

        return "".join(transformed)

    @staticmethod
    def _build_cumulative_array(text: str) -> dict[str, int]:
        """
        Construct the cumulative frequency array C.

        C[c] is the number of characters in the text that are
        alphabetically smaller than c.
        """
        frequencies = Counter(text)
        cumulative: dict[str, int] = {}

        total = 0

        for char in sorted(frequencies):
            cumulative[char] = total
            total += frequencies[char]

        return cumulative

    def count(self, pattern: str) -> int:
        """
        Count the number of occurrences of pattern using backward search.
        """
        if pattern == "":
            return self.length

        left = 1
        right = self.length

        for char in reversed(pattern):
            if char not in self.cumulative:
                return 0

            left = (
                self.cumulative[char]
                + self.wavelet_tree.rank(char, left - 1)
                + 1
            )

            right = (
                self.cumulative[char]
                + self.wavelet_tree.rank(char, right)
            )

            if left > right:
                return 0

        return right - left + 1


def direct_count(text: str, pattern: str) -> int:
    """
    Count pattern occurrences by direct scanning.

    This function is used only to verify the FM index.
    """
    if pattern == "":
        return len(text)

    if len(pattern) > len(text):
        return 0

    count = 0

    for start in range(len(text) - len(pattern) + 1):
        if text.startswith(pattern, start):
            count += 1

    return count


def run_tests() -> None:
    text = "acagcagg$"
    index = FMIndex(text)

    print("Text:", index.text)
    print("Suffix array:", index.suffix_array)
    print("BWT:", index.bwt)
    print("C array:", index.cumulative)

    test_patterns = [
        "a",
        "c",
        "g",
        "cag",
        "agg",
        "gc",
        "aaa",
        "acagcagg",
    ]

    for pattern in test_patterns:
        fm_result = index.count(pattern)
        direct_result = direct_count(text, pattern)

        print(
            f"Pattern {pattern!r}: "
            f"FM index = {fm_result}, "
            f"direct scan = {direct_result}"
        )

        assert fm_result == direct_result

    assert index.suffix_array == [8, 0, 2, 5, 1, 4, 7, 3, 6]
    assert index.bwt == "g$ccaggaa"
    assert index.count("cag") == 2
    assert index.count("agg") == 1
    assert index.count("aaa") == 0

    print("All FM index tests passed.")


if __name__ == "__main__":
    run_tests()