import os
from unittest import mock

from requests import Response

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
        chats = tgmain.setup_educabiz()
        self.assertEqual(chats, {11111: [mock.ANY, mock.ANY]})
        self.assertEqual(chats[11111][0]._username, 'u1')
        self.assertEqual(chats[11111][1]._username, 'u2')

    def test_client_strips_bom_from_retried_response(self):
        response = Response()
        response._content = b'\xef\xbb\xbf{"ok": true}'

        with mock.patch.object(tgmain._EducabizClient, 'request', return_value=response):
            client = tgmain.Client('u1', 'p1', login_if_required=True)
            response = client.request('GET', '/school/qrcodeinfo')

        self.assertEqual(response.json(), {'ok': True})
