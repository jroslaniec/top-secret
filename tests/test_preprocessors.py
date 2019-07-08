from decimal import Decimal

from top_secret import base64preprocessor, base32preprocessor, typed_preprocessor


def test_base64_preprocessor():
    encoded_secret = "c2VjcmV0"
    result = base64preprocessor(encoded_secret)
    assert result == "secret"


def test_base32_preprocessor():
    encoded_secret = "ONSWG4TFOQ======"
    result = base32preprocessor(encoded_secret)
    assert result == "secret"


def test_types_preprocessor_int_1():
    encoded = "i:10"
    result = typed_preprocessor(encoded)
    assert result == 10


def test_types_preprocessor_int_2():
    encoded = "int:10"
    result = typed_preprocessor(encoded)
    assert result == 10


def test_types_preprocessor_float_1():
    encoded = "f:10.19"
    result = typed_preprocessor(encoded)
    assert result == 10.19


def test_types_preprocessor_float_2():
    encoded = "float:10.19"
    result = typed_preprocessor(encoded)
    assert result == 10.19


def test_types_preprocessor_decimal_1():
    encoded = "d:10.30303"
    result = typed_preprocessor(encoded)
    assert result == Decimal("10.30303")


def test_types_preprocessor_decimal_2():
    encoded = "decimal:10.30303"
    result = typed_preprocessor(encoded)
    assert result == Decimal("10.30303")


def test_types_preprocessor_bool_1():
    encoded = "b:0"
    result = typed_preprocessor(encoded)
    assert result is False


def test_types_preprocessor_bool_2():
    encoded = "b:1"
    result = typed_preprocessor(encoded)
    assert result is True


def test_types_preprocessor_string_1():
    encoded = "s:hello"
    result = typed_preprocessor(encoded)
    assert result == "hello"


def test_types_preprocessor_string_2():
    encoded = "string:hello"
    result = typed_preprocessor(encoded)
    assert result == "hello"


def test_types_preprocessor_json_1():
    encoded = 'j:{"hello": "world"}'
    result = typed_preprocessor(encoded)
    assert result == {"hello": "world"}


def test_types_preprocessor_json_2():
    encoded = 'json:{"hello": "world"}'
    result = typed_preprocessor(encoded)
    assert result == {"hello": "world"}
