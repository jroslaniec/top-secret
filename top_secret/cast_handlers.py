from .exceptions import CastError


def bool_cast_handler(value):
    if isinstance(value, bool):
        return value

    value = value.lower()
    if value in ("true", "yes", "1"):
        return True
    if value in ("false", "no", "0"):
        return False

    raise CastError
