import os
import shutil

import pytest

from top_secret import FileSecretSource, DirectorySecretSource
from top_secret import SecretMissingError

SECRET_BASE_PATH = os.path.join("/tmp", ".top_secret_test")


@pytest.fixture(scope="module", autouse=True)
def setup_teardown_module():
    # Setup
    os.makedirs(SECRET_BASE_PATH, exist_ok=True)

    yield

    # Tear Down
    if os.path.exists(SECRET_BASE_PATH):
        shutil.rmtree(SECRET_BASE_PATH)


@pytest.fixture(autouse=True)
def setup_function():
    for file in os.listdir(SECRET_BASE_PATH):
        path = os.path.join(SECRET_BASE_PATH, file)
        if os.path.isfile(path):
            os.unlink(path)


def test_file_ss_raise_if_file_does_not_exist():
    ss = DirectorySecretSource(SECRET_BASE_PATH)
    with pytest.raises(SecretMissingError):
        ss.get("missing.txt")


def test_file_ss_exists():
    ss = DirectorySecretSource(SECRET_BASE_PATH)

    with open(os.path.join(SECRET_BASE_PATH, "my_secret.txt"), "w") as fd:
        fd.write("secret")

    secret = ss.get("my_secret.txt")
    assert secret == "secret"


def test_file_ss_stripes_whitespaces():
    ss = DirectorySecretSource(SECRET_BASE_PATH)

    with open(os.path.join(SECRET_BASE_PATH, "my_secret.txt"), "w") as fd:
        fd.write("\t\n secret\t \n\n")

    secret = ss.get("my_secret.txt")
    assert secret == "secret"


def test_file_ss_with_whitespace_striping():
    ss = DirectorySecretSource(SECRET_BASE_PATH, stripe_whitespaces=False)

    secret_in_file = "\t\n secret\t \n\n"
    with open(os.path.join(SECRET_BASE_PATH, "my_secret.txt"), "w") as fd:
        fd.write(secret_in_file)

    secret = ss.get("my_secret.txt")
    assert secret == secret_in_file


def test_file_ss_postfix():
    ss = DirectorySecretSource(SECRET_BASE_PATH, postfix=".txt")

    with open(os.path.join(SECRET_BASE_PATH, "my_secret.txt"), "w") as fd:
        fd.write("secret")
    secret = ss.get("my_secret")
    assert secret == "secret"


def test_file_ss_get_secret_by_asb_path():
    ss = DirectorySecretSource(SECRET_BASE_PATH)

    path = os.path.join(SECRET_BASE_PATH, "my_secret.txt")
    secret_in_file = "secret"
    with open(path, "w") as fd:
        fd.write(secret_in_file)

    secret = ss.get(path)
    assert secret == secret_in_file
