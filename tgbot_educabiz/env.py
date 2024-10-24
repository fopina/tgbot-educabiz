import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()


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


env = Env()
