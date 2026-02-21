from collections.abc import Callable, Iterable
from functools import cache, reduce
from itertools import product
from typing import Type, override

from flat.peekiter import PeekIterator, peek


class NontermSym(str):
    @override
    def __repr__(self) -> str:
        return f"NTerm({str(self)})"


class TermSym(str):
    @override
    def __repr__(self) -> str:
        return f"TTerm({str(self)})"


Symbol = NontermSym | TermSym


def TTerms(*terms: str) -> Iterable[TermSym]:
    return sorted(TermSym(t) for t in terms)


EPSILON = NULLSTR = TermSym("ϵ")
EOF = TermSym("$")


class Production:
    lhs: NontermSym
    rhs: list[TermSym | NontermSym]

    @override
    def __eq__(self, value: object, /) -> bool:
        match value:
            case Production() as p:
                return self.lhs == value.lhs and self.rhs == value.rhs
            case _:
                raise TypeError("!")

    def __init__(self, lhs: NontermSym | str, *rhs: NontermSym | TermSym) -> None:
        self.lhs = lhs if isinstance(lhs, NontermSym) else NontermSym(lhs)
        self.rhs = list(rhs)

    def __str__(self) -> str:
        return f"{self.lhs} = {'·'.join(self.rhs)}"

    def __repr__(self) -> str:
        return str(self)

    def is_empty(self) -> bool:
        return len(self.rhs) == 1 and self.rhs[0] == EPSILON

    @override
    def __hash__(self) -> int:
        return hash((self.lhs, *self.rhs))


class Grammar:
    nonterms: set[NontermSym]
    terms: set[TermSym]
    start: NontermSym
    prods: set[Production]

    def __init__(
        self,
        N: Iterable[NontermSym],
        T: Iterable[TermSym],
        S: NontermSym,
        P: Iterable[Production],
    ) -> None:

        assert S in N and reduce(bool.__or__, (S == p.lhs for p in P))

        self.nonterms = set(N)
        self.terms = set(T)
        self.start = S
        self.prods = set(P)

        assert self.terms.isdisjoint(self.nonterms)

    @override
    def __str__(self) -> str:
        p1 = list(sorted(map(str, self.prods)))
        p2 = [p1[0]]
        for i, j in zip(p1[:-1], p1[1:]):
            il, ir = i.split(" = ")
            jl, jr = j.split(" = ")
            if il == jl:
                p2.append(" " * len(jl) + " | " + jr)
            else:
                p2.append(j)
        return "Grammar:\n  " + "\n  ".join(p2)

    def FIRST(self, nt: NontermSym | Production) -> set[TermSym]:
        if isinstance(nt, Production):
            match nt.rhs[0]:
                case TermSym() as a:
                    return {a}
                case NontermSym() as A:
                    return self.FIRST(A)
        else:
            s: set[TermSym] = set()
            return s.union(*(self.FIRST(p) for p in self.prods if p.lhs == nt))

    def get_productions(self, A: NontermSym) -> set[Production]:
        return {p for p in self.prods if p.lhs == A}

    def _chose_production(self, A: NontermSym, a: TermSym) -> Production | None:
        for p in self.get_productions(A):
            if a in self.FIRST(p):
                return p

        for p in self.get_productions(A):
            if EPSILON in self.FIRST(p):
                return p

    def recognize(
        self, scanner: PeekIterator[TermSym], start: NontermSym | None = None
    ):
        """LL(1)"""
        if start is None:
            p = Production(NontermSym("<START>"), self.start, EOF)
        else:
            p = self._chose_production(start, peek(scanner))

        if p is None:
            raise Exception("Could not find production")

        print(p.lhs + "(", end="")
        for symb in p.rhs:
            match symb:
                case TermSym("ϵ"):
                    print("ϵ", end="")
                    continue
                case TermSym("$"):
                    if (t := next(scanner, None)) is not None:
                        raise Exception(f"Expected EOF but found '{t}'")
                    else:
                        print("$", end="")

                case TermSym() as a:
                    if a != EPSILON and (
                        (t := next(scanner)) != a or print(t, end="") is not None
                    ):
                        raise Exception(f"Expected '{a}' but found '{t}'")
                case NontermSym() as A:
                    self.recognize(scanner, A)
        print(")", end="")


if __name__ == "__main__":
    s, sp = NontermSym("S"), NontermSym("S'")
    a, b, c, d = TTerms("a", "b", "c", "d")
    p1 = Production(s, a, s, d)
    p2 = Production(s, sp)
    p3 = Production(sp, b, sp, c)
    p4 = Production(sp, EPSILON)
    g = Grammar([s, sp], [a, b, c, d], s, [p1, p2, p3, p4])

    p = "aaa"
    u = "abcd"
    s = "ddd"
    # w = "a" * 10 + "b" * 5 + "c" * 5 + "d" * 10
    w = p + u + s
    print(g)
    g.recognize(PeekIterator(map(TermSym, w)))
    print()
