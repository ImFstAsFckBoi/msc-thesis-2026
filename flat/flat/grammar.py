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
    rhs: list[TTerm | NTerm]

    def __init__(self, lhs: NTerm | str, *rhs: NTerm | TTerm) -> None:
        self.lhs = lhs if isinstance(lhs, NTerm) else NTerm(lhs)
        self.rhs = list(rhs)

    def __str__(self) -> str:
        return f"{self.lhs} = {'·'.join(self.rhs)}"


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
        p1 = sorted(map(str, self.prods))
        p2 = [p1[0]]
        for i, j in zip(p1[:-1], p1[1:]):
            il, ir = i.split(" = ")
            jl, jr = j.split(" = ") 
            if il == jl:
                p2.append(" "*len(jl)+" | "+jr)
            else:
                p2.append(j)
        return "Grammar:\n  " + "\n  ".join(p2)


def _flatten_term(symb: NTerm | TTerm, *states: int) -> NTerm | TTerm:
    return type(symb)(f"{symb}({','.join(map(str, states))})")



def flatten(p: int, q: int, G: Grammar):
    fa = FAGeneric(p, q)

    N1 = {
        _flatten_term(A+"⊕", i, j)
        for A, i, j in product(G.nonterms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N2 = {
        _flatten_term(a+"⊕", i, j)
        for a, i, j in product(G.terms, fa.S(), fa.S())
        if j in fa.closure(i)
    }

    N3 = {
        _flatten_term(NTerm(EPSILON+"⊕"), i, j) for i, j in product(fa.S(), fa.S()) if j in fa.closure(i)
    }

    N: set[NTerm] = set.union(N1, N2, N3)

    P1 = {
        Production(_flatten_term(p.lhs+"⊕", i, j), *map(lambda x: _flatten_term(x, i, j),  p.rhs)) for p, i, j in product(G.prods, fa.S(), fa.S()) if j in fa.closure(i)
    }

    P2 = {
        Production(_flatten_term(NTerm(a+"⊕"), i, j), *(_flatten_term("ϵ⊕", i, i_1), _flatten_term(a, i_1), _flatten_term("ϵ⊕", i_2, j)))
        for a, i, j, i_1, i_2 in product(G.terms, fa.S(), fa.S(), fa.S(), fa.S())
        if j in fa.closure(i) and i_1 in fa.closure(i) and i_2 == fa.loop_succ(i_1) and j in fa.closure(i_2)}

    P31 = {
        Production(_flatten_term("ϵ⊕", i, j), _flatten_term("ϵ", i), _flatten_term("ϵ⊕", k, j))
        for i, j, k in product(fa.S(), fa.S(), fa.S())
        if k == fa.loop_succ(i) and j in fa.closure(k)
    }

    P32 = {Production(_flatten_term("ϵ⊕", i, i), EPSILON) for i in fa.S()}

    
    P4 = {
        Production(_flatten_term(A, i, fa.entry_succ(i)), EPSILON)
        for A, i in product(G.nonterms, fa.non_acc_entries())
    }


    P = set.union(P1, P2, P31, P32, P4)

    T = {f"{a}({i})" for a, i in product(G.terms.union({EPSILON}), fa.S())}.union({EPSILON})
    S = NTerm(f"S(1,{len(fa)})")

    return Grammar(N, T, P, S)


if __name__ == "__main__":
    s = NTerm("S")
    a, b = TTerm("a"), TTerm("b")

    p = Production(s, a, b)

    g = Grammar([s], [a, b], [p], s)

    gp = flatten(3, 2, g)
    print(g)
    print(gp)
