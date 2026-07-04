import asyncio
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
        self.assertEqual(co.entry_out.time, '17:11')

        ci = PresenceCheck.model_validate(check_in_response)
        self.assertEqual(ci.hasIn, True)
        self.assertEqual(ci.hasOut, False)
        self.assertEqual(ci.entry_in.time, '09:52')
        self.assertEqual(ci.entry_out.time, '')

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
