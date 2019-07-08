# top_secret

Small python library for getting secret from various places like environment variables or files.

**Only Python >= 3.6.0 is supported**

# Installation

```bash
pip install git+https://github.com/jroslaniec/top-secret@0.2.0#egg=top_secret
```

# Motivation

More times than not you need some secrets in your application.
There are many ways to store then and in each case, there is different retrieval method.
For example, you may store your secrets in environment variables or files or even get them from some HTTP server.
Even if you store all your secrets in environment variables the problem with encoding or type may arise.
Let's say you store your database password in base64.
It's not hard to decode that, but it can get messy and
redundant to specify that everywhere.

So, this small package is here to help you to make it a little easier and unified.


# Examples

By default, secrets are retrieved from environment variables.

```python
import os
from top_secret import vault

os.environ['MY_SECRET'] = '10'

assert vault.get('MY_SECRET') == '10'
assert vault.get('MY_SECRET', no_cache=True, cast_to=int) == 10

os.environ['MY_SECRET_2'] = 'True'
assert vault.get('MY_SECRET_2', cast_to=bool) == True
```

Load secret in json:

```python
import os
import base64
import json

from top_secret import vault, base64preprocessor

vault.add_preprocessor(base64preprocessor)

secret = base64.b64encode(b'{"hello": "world"}').decode()
os.environ['MY_SECRET'] = secret

assert vault.get('MY_SECRET', cast_to=json.loads) == {'hello': 'world'}
```

Load secrets from a file with type annotations:

```bash
# bash

cd /tmp
echo "int:10" > magic_number.txt
echo "json:{\"hello\": \"world\"}" > hello.txt
```

```python
# python

from top_secret import vault, DirectorySecretSource, typed_preprocessor

vault.add_secret_source(DirectorySecretSource('/tmp', postfix='txt'))
vault.add_preprocessor(typed_preprocessor)

assert vault.get('magic_number') == 10
assert vault.get('hello') == {'hello': 'world'}
```

# Tests

Remember to install dev requirements and simply run:
```bash
pytest
```
