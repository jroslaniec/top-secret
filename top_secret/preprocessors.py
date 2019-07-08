import base64
import json
from decimal import Decimal

from .cast_handlers import bool_cast_handler


def base64preprocessor(value):
    return base64.b64decode(value).decode()


def base32preprocessor(value):
    return base64.b32decode(value).decode()


def typed_preprocessor(value) -> "str":
    tpl = value.split(":", 1)
    if len(tpl) == 1:
        return tpl[0]

    type, value = tpl

    handler = {
        "i": int,
        "int": int,
        "f": float,
        "float": float,
        "d": Decimal,
        "decimal": Decimal,
        "b": bool_cast_handler,
        "bool": bool_cast_handler,
        "s": str,
        "string": str,
        "j": json.loads,
        "json": json.loads,
    }[type]

    return handler(value)
