from tgbot_educabiz.bot import PresenceCheck

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
