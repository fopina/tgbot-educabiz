#!/usr/bin/env -S python3 -u

import logging

from educabiz.client import Client

from .bot import Bot
from .env import env

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def setup_educabiz():
    ebs = {}
    logins = env.group('TGEB_LOGIN_')

    for k, v in logins.items():
        profile, key = k.split('_', 1)
        if profile not in ebs:
            ebs[profile] = Client()
        if key == 'USERNAME':
            ebs[profile]._username = v
        elif key == 'PASSWORD':
            ebs[profile]._password = v

    chat_map = {}
    chat_ids = env.group('TGEB_CHATID_')
    for k, v in chat_ids.items():
        profiles = v.split(',')
        k = int(k)
        chat_map[k] = []
        for profile in profiles:
            if profile not in ebs:
                raise Exception(f'{profile} not defined, review your environment')
            chat_map[k].append(ebs[profile])

    return chat_map


def main() -> None:
    """Start the bot."""

    chat_ids = setup_educabiz()

    bot = Bot(
        env('TGEB_TOKEN'),
        webhook_port=env('TGEB_WEBHOOK_PORT', 9999),
        webhook_url=env('TGEB_WEBHOOK_URL'),
        chat_ids=chat_ids,
    )
    bot.run()


if __name__ == '__main__':
    main()
