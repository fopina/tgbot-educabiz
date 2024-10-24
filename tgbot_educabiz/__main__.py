#!/usr/bin/env -S python3 -u

import logging

from .bot import Bot
from .env import env

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    bot = Bot(
        env('TGEB_TOKEN'),
        webhook_port=env('TGEB_WEBHOOK_PORT', 9999),
        webhook_url=env('TGEB_WEBHOOK_URL'),
    )
    bot.run()


if __name__ == '__main__':
    main()
