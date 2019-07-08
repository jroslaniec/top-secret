from typing import List, Dict, Callable

from .cast_handlers import bool_cast_handler
from .exceptions import CastHandlerMissingError
from .exceptions import SecretMissingError
from .exceptions import SecretSourceMissing
from .secret_sources import BaseSecretSource
from .secret_sources import EnvironmentVariableSecretSource


class NoDefault:
    pass


DEFAULT_SECRET_SOURCES = [EnvironmentVariableSecretSource()]

DEFAULT_CAST_HANDLERS = {bool: bool_cast_handler}


class Vault:
    _cache = {}
    cast_handlers: "Dict[Callable]" = {}
    secret_sources: "List[BaseSecretSource]" = []
    preprocessors: "List[Callable[str, str]]" = []

    def __init__(self, secret_sources=None, cast_handlers=None, preprocessors=None):
        if cast_handlers is None:
            cast_handlers = {}
        if secret_sources is None:
            secret_sources = []
        if preprocessors is None:
            preprocessors = []

        self.default_secret_sources = secret_sources
        self.default_cast_handlers = cast_handlers
        self.default_preprocessors = preprocessors

        self.reset()

    def add_secret_source(self, source: "BaseSecretSource"):
        if source in self.secret_sources:
            return
        self.secret_sources.append(source)

    def clear_secret_sources(self):
        self.secret_sources = []

    def reset_secret_sources(self):
        self.secret_sources = list(self.default_secret_sources)

    def add_cast_handler(self, handler_key, handler):
        self.cast_handlers[handler_key] = handler

    def clear_cast_handlers(self):
        self.cast_handlers = {}

    def reset_cast_handlers(self):
        self.cast_handlers = {**self.default_cast_handlers}

    def add_preprocessor(self, fn):
        self.preprocessors.append(fn)

    def clear_preprocessors(self):
        self.preprocessors = []

    def reset_preprocessors(self):
        self.preprocessors = list(self.default_preprocessors)

    def clear_cache(self):
        self._cache = {}

    def reset(self):
        self.reset_secret_sources()
        self.reset_cast_handlers()
        self.reset_preprocessors()
        self.clear_cache()

    def get(
        self,
        name,
        default=NoDefault,
        *,
        source=None,
        preprocessors=None,
        cast_to=None,
        no_cache=False,
        cache_result=True,
    ):
        if no_cache is False and name in self._cache:
            return self._cache[name]

        value = self._get_from_source(name, default, source)
        value = self._preprocess(value, preprocessors)
        value = self._cast_to(value, cast_to, default)

        if cache_result:
            self._cache[name] = value
        return value

    def _get_from_source(self, name, default, source):
        if source is not None:
            return source.get(name)

        if not self.secret_sources:
            raise SecretSourceMissing

        for source in self.secret_sources:
            try:
                value = source.get(name)
                break
            except SecretMissingError:
                pass
        else:
            if default is NoDefault:
                raise SecretMissingError(name)
            else:
                value = default

        return value

    def _preprocess(self, value, preprocessors):
        if preprocessors is None:
            preprocessors = self.preprocessors
        else:
            preprocessors = preprocessors

        for preprocessor in preprocessors:
            value = preprocessor(value)
        return value

    def _cast_to(self, value, cast_to, default):
        if value is default:
            return value

        if cast_to is not None:

            handler = self.cast_handlers.get(cast_to, cast_to)

            if not callable(handler):
                raise CastHandlerMissingError(
                    f"Cast handler: {handler!r}, is not registered."
                )

            value = handler(value)

        return value


vault = Vault(DEFAULT_SECRET_SOURCES, DEFAULT_CAST_HANDLERS)
