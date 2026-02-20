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


def _flatten_term(symb: NTerm | TTerm, *states: int) -> NTerm | TTerm:
    return type(symb)(f"{symb}({','.join(map(str, states))})")


def flatten(p: int, q: int, G: Grammar):
    fa = FAGeneric(p, q)

    N1 = {
        _flatten_term(A + "⊕", i, j)
        for A, i, j in product(G.nonterms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N2 = {
        _flatten_term(a + "⊕", i, j)
        for a, i, j in product(G.terms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N3 = {
        _flatten_term(NTerm(EPSILON + "⊕"), i, j)
        for i, j in product(fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N: set[NTerm] = set.union(N1, N2, N3)

    P1 = {
        Production(
            _flatten_term(p.lhs + "⊕", i, j),
            *map(lambda x: _flatten_term(x, i, j), p.rhs),
        )
        for p, i, j in product(G.prods, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    P2 = {
        Production(
            _flatten_term(NTerm(a + "⊕"), i, j),
            *(
                _flatten_term("ϵ⊕", i, i_1),
                _flatten_term(a, i_1),
                _flatten_term("ϵ⊕", i_2, j),
            ),
        )
        for a, i, j, i_1, i_2 in product(G.terms, fa.S(), fa.S(), fa.S(), fa.S())
        if j in fa.closure(i)
        and i_1 in fa.closure(i)
        and i_2 == fa.loop_succ(i_1)
        and j in fa.closure(i_2)
    }

    P31 = {
        Production(
            _flatten_term("ϵ⊕", i, j), _flatten_term("ϵ", i), _flatten_term("ϵ⊕", k, j)
        )
        for i, j, k in product(fa.S(), fa.S(), fa.S())
        if k == fa.loop_succ(i) and j in fa.closure(k)
    }

    P32 = {Production(_flatten_term("ϵ⊕", i, i), EPSILON) for i in fa.S()}

    P4 = {
        Production(_flatten_term(A, i, fa.entry_succ(i)), EPSILON)
        for A, i in product(G.nonterms, fa.non_acc_entries())
    }

    P = set.union(P1, P2, P31, P32, P4)

    T = {f"{a}({i})" for a, i in product(G.terms.union({EPSILON}), fa.S())}.union(
        {EPSILON}
    )
    S = NTerm(f"S(1,{len(fa)})")

    return Grammar(N, T, P, S)


if __name__ == "__main__":
    fl = FlatLanguage(3, 2, "ab", "abc")
    print(fl)

    g = FAGeneric(3, 2)
    print(g)

    print("Entries:", g.entries())

    for i in g.S():
        print(f"closure({i}) =", g.closure(i))
