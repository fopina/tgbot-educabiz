import os
from unittest import TestCase


class Base(TestCase):
    def setUp(self) -> None:
        # make sure environ is clean
        self._environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self) -> None:
        os.environ.update(self._environ)
