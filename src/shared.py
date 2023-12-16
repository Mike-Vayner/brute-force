import argparse
import re
import string
import sys
from functools import cache
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    IPvAnyAddress,
    ValidationError,
    ValidationInfo,
    field_validator,
)


class ConnectionArgs(BaseModel):
    host: IPvAnyAddress
    port: int = Field(ge=1024, lt=655536)
    tls: bool


class Request(BaseModel):
    start: str
    stop: str
    digest: str = Field(pattern=r"^[a-f\d]{32}$")
    charset: str = string.ascii_lowercase

    @field_validator("charset")
    @classmethod
    def ensure_charset(cls, v: str):
        assert all(
            not char.isspace() and v.count(char) == 1 for char in v
        ), "Charset must not contain repeating charcaters"
        return v

    @field_validator("start", "stop")
    @classmethod
    def matches_charset(cls, v: str, info: ValidationInfo):
        assert re.fullmatch(
            rf"^[{cls.charset}]+$", v
        ), f"{info.field_name} does not match the provided charset"


CONNECTION_PARSER = argparse.ArgumentParser(add_help=False)
CONNECTION_PARSER.add_argument("--host", default="::")
CONNECTION_PARSER.add_argument("--port", default=7200, type=int)
CONNECTION_PARSER.add_argument("--tls", action="store_true")


def get_and_validate_args[T: BaseModel](
    parser: argparse.ArgumentParser, model_type: type[T]
) -> T:
    args = parser.parse_args()
    try:
        return model_type.model_validate(vars(args))
    except ValidationError as err:
        print(err)
        sys.exit(1)


def replace_at(source: str, index: int, replace: str):
    return f"{source[:index]}{replace}{source[index + 1 :]}"


@cache
def str_increment(source: str, charset: str = string.ascii_lowercase):
    source = source[::-1]
    for index, char in enumerate(source):
        source = replace_at(
            source, index, charset[i := (charset.find(char) + 1) % len(charset)]
        )
        if i != 0:
            return source[::-1]
    return (len(source) + 1) * charset[0]


class Success(BaseModel):
    status: Literal[200] = 200
    body: str


class Fail(BaseModel):
    status: Literal[404] = 404


class Response(BaseModel):
    state: Success | Fail = Field(discriminator="status")
