from functools import reduce
from math import ceil

from flat.regex import REConcat, REKleene


class FlatLanguage(REConcat):
    p: int
    q: int

    def __init__(self, p: int, q: int, *words: str) -> None:
        self.p, self.q = p, q

        assert len(words) == q

        for w in words:
            assert len(w) <= p

        super().__init__(*(REKleene(w) for w in words))


class FAGeneric:
    p: int
    q: int

    def __init__(self, p: int, q: int) -> None:
        self.p, self.q = p, q

    def __len__(self) -> int:
        return self.p * self.q

    def S(self) -> set[int]:
        return {i for i in range(1, len(self) + 1)}

    def acc(self) -> int:
        return len(self) - self.p + 1

    def is_acc(self, i: int) -> int:
        return i == self.acc()

    def entries(self) -> set[int]:
        return {i for i in range(1, self.acc() + self.p, self.p)}

    def non_acc_entries(self) -> set[int]:
        return {i for i in range(1, self.acc(), self.p)}

    def is_entry(self, i: int) -> bool:
        return i % self.p == 1

    def loop_succ(self, i: int) -> int:
        return i - self.p + 1 if i % self.p == 0 else i + 1

    def entry_succ(self, i: int) -> int:
        if not self.is_entry(i):
            raise Exception(f"Sate '{i}' not an entry state!")

        return i + self.p

    def succ(self, i: int) -> set[int]:
        if self.is_entry(i) and i != self.acc():
            return {self.loop_succ(i), self.entry_succ(i)}
        else:
            return {self.loop_succ(i)}

    def loop(self, i: int) -> int:
        return ceil(i / 3)

    def loop_states(self, s: int) -> set[int]:
        e = 1 + self.p * (s - 1)
        return {i for i in range(e, e + self.p)}

    def closure(self, i: int) -> set[int]:
        l = self.loop(i)
        return reduce(
            set.union, (self.loop_states(s) for s in range(l, self.q + 1))
        ) - {i}


if __name__ == "__main__":
    fl = FlatLanguage(3, 2, "ab", "abc")
    print(fl)

    g = FAGeneric(3, 2)
    print(g)

    print("Entries:", g.entries())

    for i in g.S():
        print(f"closure({i}) =", g.closure(i))
