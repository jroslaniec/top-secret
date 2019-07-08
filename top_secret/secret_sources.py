import abc
import json
import os
from typing import Optional, List, Dict

import yaml

from .exceptions import SecretMissingError
from .exceptions import TopSecretError


class BaseSecretSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, name):
        pass


class EnvironmentVariableSecretSource(BaseSecretSource):
    def __init__(self, allowed_prefixes: "Optional[List[str]]" = None):
        self.allowed_prefixes = allowed_prefixes or [""]

    def get(self, name: "str") -> "str":
        value = None

        for prefix in self.allowed_prefixes:
            value = os.environ.get(f"{prefix}{name}")
            if value is not None:
                break

        if value is None:
            raise SecretMissingError(
                f"Cannot get secret {name!r}. "
                f"Environment variable {name!r} is not set."
            )
        return value


DEFAULT_SECRET_FILES = frozenset(
    ["settings.json", ".secrets.json", "settings.yaml", ".secrets.yaml"]
)


class FileSecretSource(BaseSecretSource):
    def __init__(self, files=DEFAULT_SECRET_FILES, require_files_exists=False):
        self.contents = []
        self.require_files_exists = require_files_exists

        for f in files:
            out = self._parse_file(f)
            if out is not None:
                self.contents.append(out)

    def get(self, name):
        value = None

        for c in self.contents:
            value = c.get(name)
            if value is not None:
                break

        if value is None:
            raise SecretMissingError(f"Cannot get secret {name!r}.")

        return value

    def _parse_file(self, filename):
        file_path = self._get_file_path(filename)

        file_exists = os.path.exists(file_path)
        if not file_exists and self.require_files_exists:
            raise TopSecretError(f"File {file_path} doesn't exist.")

        if not file_exists:
            return None

        if not os.path.isfile(file_path):
            raise TopSecretError(f"{file_path} is not a file.")

        ext = file_path.split(".")[-1]

        if ext == "json":
            return self._parse_json(file_path)
        if ext in ("yaml", "yml"):
            return self._parse_yaml(file_path)

        raise TopSecretError(f"File {file_path} is not in a supported format.")

    def _get_file_path(self, filename):
        if os.path.isabs(filename):
            return os.path.normpath(filename)
        return os.path.normpath(os.path.join(os.getcwd(), filename))

    def _parse_json(self, file_path):
        with open(file_path) as fd:
            return json.load(fd)

    def _parse_yaml(self, file_path):
        with open(file_path) as fd:
            return yaml.safe_load(fd.read())


class DirectorySecretSource(BaseSecretSource):
    def __init__(self, base_path, postfix=None, stripe_whitespaces=True):
        self.base_path = base_path
        self.postfix = postfix
        self.stripe_whitespaces = stripe_whitespaces

    def get(self, name, stripe_whitespaces=None):
        path = self.build_path(name)
        self.raise_on_no_file(path, name)
        secret = self.read_secret(path, stripe_whitespaces)
        return secret

    def build_path(self, name):
        if self.postfix:
            name = "{}.{}".format(name, self.postfix.lstrip("."))

        if os.path.isabs(name):
            return name
        return os.path.join(self.base_path, name)

    def raise_on_no_file(self, path, name):
        if not os.path.exists(path):
            raise SecretMissingError(
                f"Cannot get secret {name!r}. " f"File {path} doesn't exist."
            )

    def read_secret(self, path, stripe_whitespaces):
        with open(path) as fd:
            secret = fd.read()

        if stripe_whitespaces is None:
            stripe_whitespaces = self.stripe_whitespaces

        if stripe_whitespaces:
            secret = secret.strip()

        return secret


class S3FileFileSource(BaseSecretSource):
    loaded: bool
    contents: List[Dict]
    bucket_name: str
    file_names: List[str]

    def __init__(self, bucket_name: str, file_names: List[str], lazy=True):
        self.loaded = False
        self.contents = []
        self.bucket_name = bucket_name
        self.file_names = file_names

        if not lazy:
            self._load_configs()

    def get(self, name):
        if not self.loaded:
            self._load_configs()

        value = None

        for c in self.contents:
            value = c.get(name)
            if value is not None:
                break

        if value is None:
            raise SecretMissingError(f"Cannot get secret {name!r}.")

        return value

    def _load_configs(self):
        import boto3

        s3 = boto3.resource("s3")
        bucket = s3.Bucket(self.bucket_name)

        for f in self.file_names:
            body = (
                bucket.objects.filter(Prefix=f)
                .__iter__()
                .__next__()
                .get()["Body"]
                .read()
            )
            c = self._parse_yaml(body)
            self.contents.append(c)

        self.loaded = True

    def _parse_yaml(self, body: bytes) -> Dict:
        return yaml.safe_load(body)
