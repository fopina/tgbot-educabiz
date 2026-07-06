import asyncio
import json
from types import SimpleNamespace
from unittest import mock

from tgbot_educabiz.bot import Bot, PresenceCheck

from . import Base


class Test(Base):
    def test_temporary_model(self):
        check_out_response = {
            'isAbsent': False,
            'hasIn': True,
            'hasOut': True,
            'hasNotes': False,
            'isLate': True,
            'late': '09:11',
            'isEarly': False,
            'early': '00:00',
            'islatepenaltyin': False,
            'islatepenaltyout': False,
            'in': {'time': '09:35', 'hour': 9, 'minutes': 35, 'fetcher': 'Pai'},
            'out': {'time': '17:11', 'hour': 17, 'minutes': 11, 'fetcher': 'Mãe'},
        }
        check_in_response = {
            'isAbsent': False,
            'hasIn': True,
            'hasOut': False,
            'hasNotes': False,
            'isLate': False,
            'isEarly': True,
            'early': '00:00',
            'islatepenaltyin': False,
            'islatepenaltyout': False,
            'in': {'time': '09:52', 'hour': 9, 'minutes': 52, 'fetcher': 'Pai'},
            'out': {'time': '--:--', 'hour': 0, 'minutes': 0, 'fetcher': ''},
        }

        co = PresenceCheck.model_validate(check_out_response)
        self.assertEqual(co.hasIn, True)
        self.assertEqual(co.hasOut, True)
        self.assertEqual(co.entry_in.fetcher, 'Pai')
        self.assertEqual(co.entry_out.time, '17:11')
        self.assertEqual(co.entry_out.fetcher, 'Mãe')

        ci = PresenceCheck.model_validate(check_in_response)
        self.assertEqual(ci.hasIn, True)
        self.assertEqual(ci.hasOut, False)
        self.assertEqual(ci.entry_in.time, '09:52')
        self.assertEqual(ci.entry_in.fetcher, 'Pai')
        self.assertEqual(ci.entry_out.time, '')
        self.assertEqual(ci.entry_out.fetcher, '')

    def test_start_continues_after_child_without_photo(self):
        def child(child_id, name):
            return SimpleNamespace(
                id=child_id,
                name=name,
                presence=[SimpleNamespace(id='undefined', absent=False, hourIn=None, hourOut=None)],
            )

        children = {
            'first': child('first', 'First Child'),
            'second': child('second', 'Second Child'),
        }
        eb = mock.Mock()
        eb.school_qrcodeinfo.return_value = SimpleNamespace(child=children)
        eb.home.return_value = SimpleNamespace(
            children={
                'first': SimpleNamespace(photo=None),
                'second': SimpleNamespace(photo='https://example.invalid/second.jpg'),
            }
        )

        message = mock.AsyncMock()
        update = SimpleNamespace(effective_user=SimpleNamespace(id=123), message=message)
        bot = Bot(token='token', chat_ids={123: [eb]})

        asyncio.run(bot.start(update, mock.Mock()))

        message.reply_markdown_v2.assert_awaited_once()
        message.reply_photo.assert_awaited_once()
        self.assertIn('First Child', message.reply_markdown_v2.await_args.args[0])
        self.assertIn('Second Child', message.reply_photo.await_args.kwargs['caption'])

    def test_webhook_secret_token_is_json_serializable(self):
        bot = Bot(token='token', chat_ids={})

        json.dumps({'secret_token': bot._secret_token})

    def test_run_webhook_uses_configured_listen_address(self):
        bot = Bot(
            token='token',
            webhook_url='https://example.invalid/webhook',
            webhook_port=8080,
            webhook_listen='127.0.0.1',
            chat_ids={},
        )
        application = mock.Mock()

        with mock.patch.object(bot, 'setup_app', return_value=application):
            bot.run()

        application.run_webhook.assert_called_once()
        self.assertEqual(application.run_webhook.call_args.kwargs['port'], 8080)
        self.assertEqual(application.run_webhook.call_args.kwargs['listen'], '127.0.0.1')
        self.assertEqual(
            application.run_webhook.call_args.kwargs['webhook_url'],
            'https://example.invalid/webhook',
        )
