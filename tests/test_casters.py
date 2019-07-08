import pytest

from top_secret import CastError
from top_secret.cast_handlers import bool_cast_handler


def test_bool_cast_handler():
    for value, expected in (
        ("false", False),
        ("fAlSE", False),
        ("0", False),
        ("no", False),
        (False, False),
        ("True", True),
        ("true", True),
        ("TRUE", True),
        ("YES", True),
        ("1", True),
        (True, True),
    ):
        result = bool_cast_handler(value)
        assert result is expected


def test_bool_test_handler_raise():
    with pytest.raises(CastError):
        bool_cast_handler("unknown")
