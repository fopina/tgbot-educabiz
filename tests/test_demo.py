import tgbot_educabiz

from . import Base


class Test(Base):
    def test_echo(self):
        self.assertEqual(tgbot_educabiz.version, tgbot_educabiz.version)
