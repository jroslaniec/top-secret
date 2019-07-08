import os
from base64 import b64encode

import pytest

from top_secret import (
    vault,
    SecretMissingError,
    CastHandlerMissingError,
    base64preprocessor,
    EnvironmentVariableSecretSource,
    Vault,
)
from top_secret.cast_handlers import bool_cast_handler
from top_secret.exceptions import SecretSourceMissing

ENV_VAL_TEST_PREFIX = "_TEST_TOP_SECRET"
ENV_VAL_1 = f"{ENV_VAL_TEST_PREFIX}_TEST"


@pytest.fixture(autouse=True)
def setup_function():
    keys_to_remove = [
        key for key in os.environ.keys() if key.startswith(ENV_VAL_TEST_PREFIX)
    ]

    for key in keys_to_remove:
        del os.environ[key]

    vault.reset()


def test_retrieve_secret_from_environment_variable():
    value = "Hello World"
    os.environ[ENV_VAL_1] = value

    assert vault.get(ENV_VAL_1) == value


def test_exception_raised_if_no_environment_variable_is_set():
    with pytest.raises(SecretMissingError):
        vault.get(ENV_VAL_1)


def test_retrieved_value_is_cached(mocker):
    value = "Hello World"
    os.environ[ENV_VAL_1] = value
    vault.get(ENV_VAL_1)

    mocker.patch("top_secret.vault._get_from_source")
    vault.get(ENV_VAL_1)
    vault._get_from_source.assert_not_called()


def test_retrieve_with_cast_to_int():
    value = "10"
    os.environ[ENV_VAL_1] = value
    retrieved = vault.get(ENV_VAL_1, cast_to=int)
    assert retrieved == 10


def test_retrieve_with_cast_to_float():
    value = "10.101"
    os.environ[ENV_VAL_1] = value
    retrieved = vault.get(ENV_VAL_1, cast_to=float)
    assert retrieved == 10.101


def test_retrieve_with_cast_to_bool():
    for value, expected in (
        ("false", False),
        ("fAlSE", False),
        ("0", False),
        ("no", False),
        ("True", True),
        ("true", True),
        ("TRUE", True),
        ("YES", True),
        ("1", True),
    ):
        key = f"{ENV_VAL_TEST_PREFIX}_{value}"
        os.environ[key] = value

        # Just to be sure
        vault.clear_cache()

        retrieved = vault.get(key, cast_to=bool)
        assert retrieved == expected


def test_retrieve_with_custom_cast():
    import json

    value = '{"hello": "world"}'
    os.environ[ENV_VAL_1] = value

    retrieved = vault.get(ENV_VAL_1, cast_to=json.loads)
    assert retrieved == {"hello": "world"}


def test_base64_preprocessor():
    import json
    import base64
    from top_secret import base64preprocessor

    vault.add_preprocessor(base64preprocessor)

    secret = base64.b64encode(b'{"hello": "world"}').decode()
    os.environ[ENV_VAL_1] = secret

    assert vault.get(ENV_VAL_1, cast_to=json.loads) == {"hello": "world"}


def test_ad_hoc_preprocessor():
    import json
    import base64
    from top_secret import base64preprocessor

    secret = base64.b64encode(b'{"hello": "world"}').decode()
    os.environ[ENV_VAL_1] = secret

    value = vault.get(ENV_VAL_1, cast_to=json.loads, preprocessors=[base64preprocessor])
    assert value == {"hello": "world"}


def test_get_default_if_secret_is_missing():
    result = vault.get("missing", "missing")
    assert result == "missing"


def test_raises_if_no_cast_handler_exist():
    os.environ[ENV_VAL_1] = "secret"
    with pytest.raises(CastHandlerMissingError):
        vault.get(ENV_VAL_1, cast_to="json")


def test_specify_source_in_get(mocker):
    m = mocker.Mock()
    vault.get("secret", source=m)
    m.get.asset_called_once()


def test_clear_preprocessors():
    secret = "Hello World"
    secret_encoded = b64encode(secret.encode()).decode()
    vault.add_preprocessor(base64preprocessor)

    os.environ[ENV_VAL_1] = secret_encoded

    result = vault.get(ENV_VAL_1)
    assert result == secret

    vault.clear_preprocessors()

    result = vault.get(ENV_VAL_1, no_cache=True)
    assert result == secret_encoded


def test_clear_cast_handlers():
    secret = "True"
    os.environ[ENV_VAL_1] = secret

    vault.add_cast_handler("bool", lambda x: bool_cast_handler(x))
    result = vault.get(ENV_VAL_1, cast_to="bool")
    assert result is True

    vault.clear_cast_handlers()
    with pytest.raises(CastHandlerMissingError):
        vault.get(ENV_VAL_1, no_cache=True, cast_to="bool")


def test_adding_secret_source(mocker):
    ss_mock = mocker.Mock()
    vault.add_secret_source(ss_mock)
    vault.get(ENV_VAL_1, None)
    ss_mock.get.assert_called_once()


def test_secret_source_duplicate_is_removed():
    env_ss = EnvironmentVariableSecretSource()
    vault.clear_secret_sources()
    assert len(vault.secret_sources) == 0
    vault.add_secret_source(env_ss)
    vault.add_secret_source(env_ss)
    assert len(vault.secret_sources) == 1


def test_error_is_raised_if_no_secret_source_is_present():
    empty_vault = Vault()
    with pytest.raises(SecretSourceMissing):
        empty_vault.get(ENV_VAL_1)
