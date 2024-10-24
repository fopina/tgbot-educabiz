import unittest
import tgbot_educabiz

class Test(unittest.TestCase):
    def test_echo(self):
        self.assertEqual(tgbot_educabiz.version, tgbot_educabiz.version)
