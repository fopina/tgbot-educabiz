#!/usr/bin/env -S python3 -u

import logging

from educabiz.client import Client

from .bot import Bot
from .env import env


def setup_educabiz():
    ebs = {}
    logins = env.group('TGEB_LOGIN_')

    for k, v in logins.items():
        profile, key = k.split('_', 1)
        if profile not in ebs:
            ebs[profile] = [None, None]
        if key == 'USERNAME':
            ebs[profile][0] = v
        elif key == 'PASSWORD':
            ebs[profile][1] = v

    chat_map = {}
    chat_ids = env.group('TGEB_CHATID_')
    for k, v in chat_ids.items():
        profiles = v.split(',')
        k = int(k)
        chat_map[k] = []
        for profile in profiles:
            c = ebs.get(profile)
            if c is None:
                raise Exception(f'{profile} not defined, review your environment')
            if not isinstance(c, Client):
                if not all(c):
                    raise Exception(f'{profile} missing username or password')
                c = Client(c[0], c[1], login_if_required=True)
                ebs[profile] = c
            chat_map[k].append(c)

    return chat_map


def main() -> None:
    """Start the bot."""

    # Enable logging
    if env('TGEB_DEBUG') == 'true':
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger('httpx').setLevel(logging.WARNING)

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
