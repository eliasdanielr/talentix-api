from typing import Any, TypeVar, TypeAlias, Union

from pydantic import BaseModel


class Error(BaseModel):
    message: str


class Cerror(Error):
    code: int
    domain: str
    reason: str
    details: dict[str, Any]


ReturnT = TypeVar("ReturnT")
ReturnType: TypeAlias = Union[
    tuple[ReturnT, None],
    tuple[None, Error],
]
