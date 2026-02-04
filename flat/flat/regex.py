from abc import ABC
from typing import override


class REComp(ABC): ...


class REKleene(REComp):
    comp: REComp

    def __init__(self, comp: REComp | str) -> None:

        self.comp = RETerm(comp) if isinstance(comp, str) else comp
        super().__init__()

    @override
    def __str__(self) -> str:
        return f"({self.comp})*"


class REConcat(REComp):
    comps: list[REComp]

    def __init__(self, *comps: REComp | str) -> None:
        self.comps = [
            (RETerm(comp) if isinstance(comp, str) else comp) for comp in comps
        ]
        super().__init__()

    @override
    def __str__(self) -> str:
        return f"{" · ".join(str(c) for c in self.comps)}"


class RETerm(REComp):
    symbols: str

    def __init__(self, symbols: str) -> None:
        self.symbols = symbols
        super().__init__()

    @override
    def __str__(self) -> str:
        return f"{self.symbols}"


def RE(re: str) -> REComp:
    re = re.replace("·", "++")
    presidence = ""


if __name__ == "__main__":
    re = REConcat(REKleene("ab"), REKleene("abc"))
    print(re)
