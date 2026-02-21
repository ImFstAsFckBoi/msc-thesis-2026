from collections.abc import Sequence
from functools import reduce
from typing import SupportsIndex, TypeVar, overload

T_seq, T_sen = TypeVar("T_seq"), TypeVar("T_sen")

x = {"a": 1}


@overload
def getitem[T_seq, T_sen](
    seq: Sequence[T_seq], i: int, sentinel: T_sen
) -> T_seq | T_sen: ...


@overload
def getitem[T_seq, T_sen](
    seq: Sequence[T_seq], i: slice, sentinel: T_sen
) -> Sequence[T_seq] | T_sen: ...


@overload
def getitem[T_seq, T_sen](seq: Sequence[T_seq], i: int) -> T_seq: ...


@overload
def getitem[T_seq, T_sen](seq: Sequence[T_seq], i: slice) -> Sequence[T_seq]: ...


def getitem[T_seq, T_sen](
    seq: Sequence[T_seq], i: int | slice, sentinel: T_sen = ...
) -> T_seq | Sequence[T_seq] | T_sen:
    try:
        return seq.__getitem__(i)
    except IndexError as e:
        if sentinel != Ellipsis:
            return sentinel
        else:
            raise e


def And(*clause: bool) -> bool:
    return reduce(lambda x, y: x and y, clause)


def Or(*clause: bool) -> bool:
    for c in clause:
        if c:
            return True
    return False
