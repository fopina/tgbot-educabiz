#!/usr/bin/env -S python3 -u

import logging
import os
import uuid

import dotenv
from telegram import Update

from .bot import setup_app

dotenv.load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    application = setup_app(os.getenv('TGEB_TOKEN'))

    # Run the bot until the user presses Ctrl-C
    webhook_url = os.getenv('TGEB_WEBHOOK_URL')
    if webhook_url:
        # TODO: check with upstream if random secret_token should not be handled BY DEFAULT
        secure_uuid = uuid.uuid4()
        application.run_webhook(
            port=os.getenv('TGEB_WEBHOOK_PORT', 9999),
            webhook_url=webhook_url,
            secret_token=secure_uuid,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
