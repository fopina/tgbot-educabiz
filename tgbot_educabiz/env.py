import os
from pathlib import Path

import dotenv

dotenv.load_dotenv('.env.app')


class Env:
    def __init__(self, file_suffix=True):
        self._file = file_suffix

    def __call__(self, key: str, default: str = None) -> str:
        if self._file:
            key_file = f'{key}_FILE'
            value = os.environ.get(key_file)
            if value is not None:
                return Path(value).read_text().strip()
        value = os.environ.get(key, default)
        return value

    def group(self, prefix: str) -> dict[str, str]:
        r = {}
        for key in os.environ:
            if key.startswith(prefix):
                if self._file and key.endswith('_FILE'):
                    value = self(key[:-5])
                    key = key[:-5]
                else:
                    value = self(key)
                r[key[len(prefix) :]] = value
        return r


env = Env()
