from collections.abc import Callable, Iterable
from functools import reduce
from itertools import product
from typing import override

from flat.peekiter import PeekIterator, peek


class NTerm(str):
    @override
    def __repr__(self) -> str:
        return f"NTerm({str(self)})"


class TTerm(str):
    @override
    def __repr__(self) -> str:
        return f"TTerm({str(self)})"


def TTerms(*terms: str) -> Iterable[TTerm]:
    return sorted(TTerm(t) for t in terms)


EPSILON = NULLSTR = TTerm("ϵ")
EOF = TTerm("$")


class Production:
    lhs: NTerm
    rhs: list[TTerm | NTerm]

    def __init__(self, lhs: NTerm | str, *rhs: NTerm | TTerm) -> None:
        self.lhs = lhs if isinstance(lhs, NTerm) else NTerm(lhs)
        self.rhs = list(rhs)

    def __str__(self) -> str:
        return f"{self.lhs} = {'·'.join(self.rhs)}"

    def __repr__(self) -> str:
        return str(self)

    def is_empty(self) -> bool:
        return len(self.rhs) == 1 and self.rhs[0] == EPSILON


class LR0Item:
    prod: Production
    prod_idx: int
    point: int

    def __init__(self, prod: Production, prod_idx: int, point: int) -> None:
        self.prod = prod
        self.prod_idx = prod_idx
        self.point = point

    @override
    def __hash__(self) -> int:
        return hash((self.prod_idx, self.point))

    @override
    def __eq__(self, value: object, /) -> bool:
        match value:
            case LR0Item(prod_idx=idx, point=p):
                return self.prod_idx == idx and self.point == p
            case _:
                raise TypeError(
                    f"Can not determine equality of {type(self)} and {type(value)}."
                )

    @override
    def __str__(self) -> str:
        if self.prod.is_empty():
            return f"{self.prod.lhs} -> ."
        else:
            rhs = (
                self.prod.rhs[0 : self.point]
                + [TTerm(".")]
                + self.prod.rhs[self.point :]
            )
            return f"{self.prod.lhs} -> {''.join(rhs)}"

    @override
    def __repr__(self) -> str:
        return f"{(self.prod_idx, self.point)} {self.__str__()}"


class Grammar:
    nonterms: set[NTerm]
    terms: set[TTerm]
    start: NTerm
    prods: set[Production]

    def __init__(
        self, N: Iterable[NTerm], T: Iterable[TTerm], S: NTerm, P: Iterable[Production]
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

    def lr0_items(self):
        items: list[LR0Item] = []

        for i, p in enumerate(self.prods):
            if p.is_empty():
                items.append(LR0Item(p, i, 0))
                continue

            for j in range(len(p.rhs) + 1):
                items.append(LR0Item(p, i, j))
        return items

    def FIRST(self, nt: NTerm | Production) -> set[TTerm]:
        if isinstance(nt, Production):
            match nt.rhs[0]:
                case TTerm() as a:
                    return {a}
                case NTerm() as A:
                    return self.FIRST(A)
        else:
            s: set[TTerm] = set()
            return s.union(*(self.FIRST(p) for p in self.prods if p.lhs == nt))

    def get_productions(self, A: NTerm) -> set[Production]:
        return {p for p in self.prods if p.lhs == A}

    def _chose_production(self, A: NTerm, a: TTerm) -> Production | None:
        for p in self.get_productions(A):
            if a in self.FIRST(p):
                return p

        for p in self.get_productions(A):
            if EPSILON in self.FIRST(p):
                return p

    def recognize(self, scanner: PeekIterator[TTerm], start: NTerm | None = None):
        """LL(1)"""
        if start is None:
            p = Production(NTerm("<START>"), self.start, EOF)
        else:
            p = self._chose_production(start, peek(scanner))

        if p is None:
            raise Exception("Could not find production")

        print(p.lhs + "(", end="")
        for symb in p.rhs:
            match symb:
                case TTerm("ϵ"):
                    print("ϵ", end="")
                    continue
                case TTerm("$"):
                    if (t := next(scanner, None)) is not None:
                        raise Exception(f"Expected EOF but found '{t}'")
                    else:
                        print("$", end="")

                case TTerm() as a:
                    if a != EPSILON and (
                        (t := next(scanner)) != a or print(t, end="") is not None
                    ):
                        raise Exception(f"Expected '{a}' but found '{t}'")
                case NTerm() as A:
                    self.recognize(scanner, A)
        print(")", end="")


if __name__ == "__main__":
    s, sp = NTerm("S"), NTerm("S'")
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
    g.recognize(PeekIterator(map(TTerm, w)))
    print()
    print(g.lr0_items())
