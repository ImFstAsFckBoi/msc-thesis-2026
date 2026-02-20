from collections.abc import Iterator, Sequence
from queue import Queue
from typing import Generic, TypeVar, overload, override

T = TypeVar("T")


class PeekIterator(Iterator[T], Generic[T]):
    _peek_buf: Queue[T]
    _iter: Iterator[T]

    def __init__(self, base: Iterator[T]) -> None:
        self._iter = base
        self._peek_buf = Queue()

    @overload
    def peek(self, n: int) -> Sequence[T]: ...

    @overload
    def peek(self) -> T: ...

    def peek(self, n: int = -1) -> T | Sequence[T]:
        if n < 0:
            p = next(self)
            self._peek_buf.put(p)
            return p
        else:
            out: list[T] = []
            for _ in range(n):
                p = next(self._iter)
                out.append(p)
                self._peek_buf.put(p)
            return out

    @override
    def __next__(self) -> T:
        if not self._peek_buf.empty():
            return self._peek_buf.get()

        return next(self._iter)


def peek[T](iter: PeekIterator[T]) -> T:
    return iter.peek()
