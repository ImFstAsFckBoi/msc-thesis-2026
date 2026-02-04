import re
from collections.abc import Iterable
from functools import reduce
from itertools import product

from flat.flat import FAGeneric


class NTerm(str): ...


class TTerm(str): ...


EPSILON = NULLSTR = TTerm("ϵ")


class Production:
    lhs: NTerm
    rhs: TTerm | NTerm

    def __init__(self, lhs: NTerm | str, rhs: NTerm | TTerm) -> None:
        self.lhs = lhs if isinstance(lhs, NTerm) else NTerm(lhs)
        self.rhs = rhs

    def __str__(self) -> str:
        return f"{self.lhs} ::= {self.rhs}"


class Grammar:
    nonterms: set[NTerm]
    terms: set[TTerm]
    prods: set[Production]
    start: NTerm

    def __init__(
        self, N: Iterable[NTerm], T: Iterable[TTerm], P: Iterable[Production], S: NTerm
    ) -> None:

        # assert S in N and reduce(bool.__or__, (S == p.lhs for p in P))

        self.nonterms = set(N)
        self.terms = set(T)
        self.prods = set(P)
        self.start = S

        assert self.terms.isdisjoint(self.nonterms)

    def __str__(self) -> str:
        return "Grammar:\n  " + "\n  ".join(str(p) for p in self.prods)


def flatten(p: int, q: int, G: Grammar):
    fa = FAGeneric(p, q)

    N1 = {
        NTerm(f"{A}({i},{j})")
        for A, i, j in product(G.nonterms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N2 = {
        NTerm(f"{a}({i},{j})")
        for a, i, j in product(G.terms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N3 = {
        NTerm(f"ϵ({i},{j})") for i, j in product(fa.S(), fa.S()) if j in fa.closure(i)
    }
    N: set[NTerm] = set.union(N1, N2, N3)

    for n in N:
        print(n)

    P4 = {
        Production(NTerm(f"A({i}, {fa.entry_succ(i)})"), EPSILON)
        for i in fa.non_acc_entries()
    }

    P31 = {
        Production(NTerm(f"ϵ⊕({i}, {j})"), NTerm(f"ϵ({i})ϵ⊕({k}, {j})"))
        for i, j, k in product(fa.S(), fa.S(), fa.S())
        if k == fa.loop_succ(i) and j in fa.closure(k)
    }

    P32 = {Production(NTerm(f"ϵ⊕({i}, {i})"), EPSILON) for i in fa.S()}

    P = set.union(P31, P32, P4)

    T = G.terms
    S = NTerm(f"S(1,{len(fa)})")

    return Grammar(N, T, P, S)


if __name__ == "__main__":
    s = NTerm("S")
    ab = TTerm("ab")

    p = Production(s, ab)

    g = Grammar([s], [ab], [p], s)

    gp = flatten(3, 2, g)
    print(g)
    print(gp)
