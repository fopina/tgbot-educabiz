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
