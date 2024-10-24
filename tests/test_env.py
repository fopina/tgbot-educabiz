import os
import tempfile

from tgbot_educabiz.env import env

from . import Base


class Test(Base):
    def test_normal(self):
        os.environ['TG_OL'] = '123'
        self.assertEqual(env('TG_OL'), '123')

    def test_file(self):
        with tempfile.NamedTemporaryFile(mode='r+') as f:
            f.write('testing')
            f.seek(0)
            os.environ['TG_OL_FILE'] = f.name
            self.assertEqual(env('TG_OL'), 'testing')

    def test_group(self):
        with tempfile.NamedTemporaryFile(mode='r+') as f:
            f.write('testing')
            f.seek(0)
            os.environ.update(
                {
                    'TG_OL_A_U': '1',
                    'TG_OL_A_P': '2',
                    'TG_OL_B_U': '3',
                    'TG_OL_B_P_FILE': f.name,
                }
            )
            self.assertEqual(env.group('TG_OL_'), {'A_U': '1', 'A_P': '2', 'B_U': '3', 'B_P_FILE': 'testing'})
