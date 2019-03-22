class SecretSourceMissing(Exception):
    def __init__(self, msg=None, *args):
        if msg is None:
            msg = 'Secret source is missing in the vault.'
        super(SecretSourceMissing, self).__init__(msg, *args)


class TopSecretError(Exception):
    pass


class CastHandlerMissingError(Exception):
    pass


class CastError(Exception):
    pass


class SecretMissingError(Exception):
    pass
