from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WaveletNode:
    alphabet: tuple[str, ...]
    sequence: str
    parent: Optional["WaveletNode"] = None
    branch: Optional[int] = None

    char: Optional[str] = None
    bitvector: list[int] = field(default_factory=list)
    prefix0: list[int] = field(default_factory=lambda: [0])
    prefix1: list[int] = field(default_factory=lambda: [0])
    positions0: list[int] = field(default_factory=list)
    positions1: list[int] = field(default_factory=list)

    left_chars: set[str] = field(default_factory=set)
    left: Optional["WaveletNode"] = None
    right: Optional["WaveletNode"] = None

    @property
    def is_leaf(self) -> bool:
        return len(self.alphabet) == 1


class WaveletTree:
    """A simplified wavelet tree with one based public queries."""

    def __init__(self, text: str, alphabet: Optional[list[str]] = None) -> None:
        if not text:
            raise ValueError("The input text must be nonempty.")

        if alphabet is None:
            alphabet = sorted(set(text))

        if len(set(alphabet)) != len(alphabet):
            raise ValueError("The alphabet must contain distinct characters.")

        if any(char not in alphabet for char in text):
            raise ValueError("Every text character must belong to the alphabet.")

        self.text = text
        self.alphabet = tuple(alphabet)
        self.leaves: dict[str, WaveletNode] = {}

        self.root = self._build(
            sequence=text,
            alphabet=self.alphabet,
            parent=None,
            branch=None,
        )

    def _build(
        self,
        sequence: str,
        alphabet: tuple[str, ...],
        parent: Optional[WaveletNode],
        branch: Optional[int],
    ) -> WaveletNode:
        node = WaveletNode(
            alphabet=alphabet,
            sequence=sequence,
            parent=parent,
            branch=branch,
        )

        if len(alphabet) == 1:
            node.char = alphabet[0]
            self.leaves[node.char] = node
            return node

        middle = len(alphabet) // 2
        left_alphabet = alphabet[:middle]
        right_alphabet = alphabet[middle:]
        node.left_chars = set(left_alphabet)

        left_sequence: list[str] = []
        right_sequence: list[str] = []

        count0 = 0
        count1 = 0

        for position, char in enumerate(sequence, start=1):
            if char in node.left_chars:
                bit = 0
                count0 += 1
                left_sequence.append(char)
                node.positions0.append(position)
            else:
                bit = 1
                count1 += 1
                right_sequence.append(char)
                node.positions1.append(position)

            node.bitvector.append(bit)
            node.prefix0.append(count0)
            node.prefix1.append(count1)

        node.left = self._build(
            sequence="".join(left_sequence),
            alphabet=left_alphabet,
            parent=node,
            branch=0,
        )

        node.right = self._build(
            sequence="".join(right_sequence),
            alphabet=right_alphabet,
            parent=node,
            branch=1,
        )

        return node

    def access(self, position: int) -> str:
        if position < 1 or position > len(self.text):
            raise IndexError("The position is outside the text.")

        node = self.root
        current = position

        while not node.is_leaf:
            bit = node.bitvector[current - 1]

            if bit == 0:
                current = node.prefix0[current]
                node = node.left
            else:
                current = node.prefix1[current]
                node = node.right

            if node is None:
                raise RuntimeError("Invalid wavelet tree structure.")

        if node.char is None:
            raise RuntimeError("A leaf must represent one character.")

        return node.char

    def rank(self, char: str, position: int) -> int:
        if char not in self.leaves:
            raise ValueError("The character is outside the alphabet.")

        if position < 0 or position > len(self.text):
            raise IndexError("The prefix length is outside the text.")

        node = self.root
        current = position

        while not node.is_leaf:
            if char in node.left_chars:
                current = node.prefix0[current]
                node = node.left
            else:
                current = node.prefix1[current]
                node = node.right

            if node is None:
                raise RuntimeError("Invalid wavelet tree structure.")

        return current

    def select(self, char: str, occurrence: int) -> int:
        if char not in self.leaves:
            raise ValueError("The character is outside the alphabet.")

        leaf = self.leaves[char]
        frequency = len(leaf.sequence)

        if occurrence < 1 or occurrence > frequency:
            raise IndexError("The requested occurrence does not exist.")

        node = leaf
        current = occurrence

        while node.parent is not None:
            parent = node.parent

            if node.branch == 0:
                current = parent.positions0[current - 1]
            elif node.branch == 1:
                current = parent.positions1[current - 1]
            else:
                raise RuntimeError("A nonroot node must have a branch value.")

            node = parent

        return current


if __name__ == "__main__":
    text = "acagcagg$"
    alphabet = ["$", "a", "c", "g"]
    tree = WaveletTree(text, alphabet)

    print(tree.access(6))
    print(tree.rank("g", 8))
    print(tree.select("c", 2))

    assert tree.access(6) == "a"
    assert tree.rank("g", 8) == 3
    assert tree.select("c", 2) == 5