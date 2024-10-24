#!/usr/bin/env -S python3 -u


import uuid

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class Bot:
    def __init__(
        self,
        token: str,
        webhook_url: str = None,
        webhook_port: int = None,
        chat_ids: dict[str, list[str]] = None,
    ):
        self._token = token
        self._webhook_url = webhook_url
        self._webhook_port = webhook_port
        self._secret_token = uuid.uuid4()

    # Define a few command handlers. These usually take the two arguments update and
    # context.
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf'Hi {user.mention_html()}!',
            reply_markup=ForceReply(selective=True),
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text('Help!')

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        await update.message.reply_text(update.message.text)

    def setup_app(self) -> Application:
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(self._token).build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help_command))

        # on non command i.e message - echo the message on Telegram
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
        return application

    def run(self):
        application = self.setup_app()
        # Run the bot until the user presses Ctrl-C
        if self._webhook_url:
            # TODO: check with upstream if random secret_token should not be handled BY DEFAULT
            application.run_webhook(
                port=self._webhook_port,
                webhook_url=self._webhook_url,
                secret_token=self._secret_token,
                allowed_updates=Update.ALL_TYPES,
            )
        else:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
