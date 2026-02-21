from flat.grammar import EPSILON, Grammar, NontermSym, Production, TermSym


def myster_M(G: Grammar):
    pass


def parikh(G: Grammar):
    formula: list[str] = []
    for N in G.nonterms:
        clause = f"M_G({N})"
        for i, p in enumerate(G.prods):
            if p.rhs.count(N) > 0:
                clause += f"+{p.rhs.count(N)}*y(p{i+1})"
        formula.append(f"({clause}=0)")

    for a in G.terms:
        sums: list[str] = []
        for i, p in enumerate(G.prods):
            sums.append(f"{p.rhs.count(a)}*y(p{i+1})")
        formula.append(f"x{a}=" + "+".join(sums))
    return " AND ".join(formula)


if __name__ == "__main__":

    S = NontermSym("S")
    Sp = NontermSym("S'")
    a, b, c, d = map(TermSym, ("a", "b", "c", "d"))
    p1 = Production(S, a, a, S, b)
    p2 = Production(S, Sp)
    p3 = Production(Sp, c, Sp, d)
    p4 = Production(Sp, EPSILON)
    G = Grammar([S, Sp], [a, b, c, d, EPSILON], [p1, p2, p3, p4], S)

    print(parikh(G))
