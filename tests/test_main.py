import os
from unittest import mock

from tgbot_educabiz import __main__ as tgmain

from . import Base


class Test(Base):
    def test_setup_educabiz_empty(self):
        self.assertEqual(tgmain.setup_educabiz(), {})

    def test_setup_educabiz(self):
        os.environ.update(
            {
                'TGEB_LOGIN_U1_USERNAME': 'u1',
                'TGEB_LOGIN_U1_PASSWORD': 'p1',
                'TGEB_LOGIN_U2_USERNAME': 'u2',
                'TGEB_LOGIN_U2_PASSWORD': 'p2',
                'TGEB_CHATID_11111': 'U1,U2',
            }
        )
        chats, ebs = tgmain.setup_educabiz()
        self.assertEqual(ebs, {'U1': mock.ANY, 'U2': mock.ANY})
        self.assertEqual(chats, {'11111': ['U1', 'U2']})
        self.assertEqual(ebs['U1']._username, 'u1')
        self.assertEqual(ebs['U2']._username, 'u2')
