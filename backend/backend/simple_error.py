from dataclasses import dataclass
from typing import TypeVar, Union


@dataclass(frozen=True)
class SimpleError:
    message: str


T = TypeVar("T")
Maybe = Union[SimpleError, T]
