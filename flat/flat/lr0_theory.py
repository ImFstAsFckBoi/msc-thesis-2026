from collections.abc import Callable, Iterable, Sequence
from functools import cache, reduce
from itertools import product
from pprint import pprint
from typing import SupportsIndex, override

from flat.grammar import (EPSILON, Grammar, NontermSym, Production, Symbol,
                          TermSym, TTerms)
from flat.utils import getitem

TTable = dict[Symbol, "LR0State"]


class LR0Item:
    prod: Production
    point: int

    def __init__(self, prod: Production, point: int) -> None:
        self.prod = prod
        self.point = point

    @override
    def __hash__(self) -> int:
        return hash((self.prod, self.point))

    @override
    def __eq__(self, value: object, /) -> bool:
        match value:
            case LR0Item(prod=prod, point=point):
                return self.prod == prod and self.point == point
            case _:
                raise TypeError(
                    f"Can not determine equality of types {type(self)} and {type(value)}."
                )

    @override
    def __str__(self) -> str:
        if self.prod.is_empty():
            return f"{self.prod.lhs} -> ."
        else:
            rhs = (
                self.prod.rhs[0 : self.point]
                + [TermSym(".")]
                + self.prod.rhs[self.point :]
            )
            return f"{self.prod.lhs} -> {''.join(rhs)}"

    @override
    def __repr__(self) -> str:
        return str(self)

    def prev_sym(self) -> Symbol | None:
        return getitem(self.prod.rhs, self.point - 1, None)

    def next_sym(self) -> Symbol | None:
        return getitem(self.prod.rhs, self.point, None)

    def advance(self) -> "LR0Item | None":
        if self.point < len(self.prod.rhs):
            return LR0Item(self.prod, self.point + 1)
        else:
            return None


class LR0State:
    grammar: Grammar
    kernel: set[LR0Item]

    def __init__(self, G: Grammar, *kernel: LR0Item) -> None:
        self.grammar = G
        self.kernel = set(kernel)

    def closure(self) -> set[LR0Item]:
        items = self.kernel

        while True:
            new_items: set[LR0Item] = set()
            l = len(items)
            for i in items:
                s = i.next_sym()
                if isinstance(s, NontermSym):
                    new_items.update(
                        LR0Item(p, 0) for p in self.grammar.get_productions(s)
                    )

            items = items.union(new_items)
            if len(items) == l:
                break
        return items

    def items(self) -> set[LR0Item]:
        return self.closure()

    @override
    def __eq__(self, value: object, /) -> bool:
        match value:
            case LR0State(kernel=k):
                return self.kernel == k
            case _:
                raise TypeError("!")

    @override
    def __hash__(self) -> int:
        return hash(tuple(self.kernel))

    @override
    def __repr__(self) -> str:
        return str(sorted(map(str, self.closure())))


def lr0_items(G: Grammar):
    items: list[LR0Item] = []

    for i, p in enumerate(G.prods):
        if p.is_empty():
            items.append(LR0Item(p, 0))
            continue

        for j in range(len(p.rhs) + 1):
            items.append(LR0Item(p, j))
    return items


class LR0Grammar(Grammar):
    def get_transitions(self, state: LR0State) -> TTable:
        out: TTable = {}
        for item in state.items():
            ts = item.next_sym()
            if ts is None:
                continue

            s = out.get(ts, None)
            if s is None:
                i = item.advance()
                assert i
                out[ts] = LR0State(self, i)
            else:
                i = item.advance()
                assert i
                s.kernel.add(i)

        return out


def make_table(G: LR0Grammar) -> dict[LR0State, TTable]:
    start = Production(NontermSym(f"{G.start}'"), G.start)

    start_ker = LR0Item(start, 0)
    state0 = LR0State(G, start_ker)

    table: dict[LR0State, TTable] = {}

    states = {state0}

    while states:
        s = states.pop()
        t = G.get_transitions(s)
        table[s] = t
        for s in t.values():
            if s not in table:
                states.add(s)
    return table


if __name__ == "__main__":

    A, B = NontermSym("A"), NontermSym("B")
    a, b, c, d = TTerms("a", "b", "c", "d")
    p1 = Production(A, a, A, d)
    p2 = Production(A, B)
    p3 = Production(B, b, B, c)
    p4 = Production(B, EPSILON)
    g = LR0Grammar([A, B], [a, b, c, d], A, [p1, p2, p3, p4])

    table = make_table(g)
    pprint(table)
