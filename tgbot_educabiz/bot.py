#!/usr/bin/env -S python3 -u


from typing import TYPE_CHECKING
import uuid

from telegram import ForceReply, Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

if TYPE_CHECKING:
    from educabiz.client import Client as EBClient


class Bot:
    def __init__(
        self,
        token: str,
        webhook_url: str = None,
        webhook_port: int = None,
        chat_ids: dict[str, list['EBClient']] = None,
    ):
        self._token = token
        self._webhook_url = webhook_url
        self._webhook_port = webhook_port
        self._secret_token = uuid.uuid4()
        self._chat_ids = chat_ids

    def is_authorized(self, user: User):
        return user is not None and user.id in self._chat_ids
    
    def get_chat_ids(self, user: User):
        return self._chat_ids.get(user.id) or []

    # Define a few command handlers. These usually take the two arguments update and
    # context.
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        if not self.is_authorized(user):
            return
        ebs = self.get_chat_ids(user)
        for eb in ebs:
            # FIXME: handle this in python-educabiz
            eb.login(eb._username, eb._password)
        for eb in ebs:
            data = eb.home()
            #print(f'School: {data["schoolname"]}')
            for child_id, child in data['children'].items():
                print(f'{child_id}:')
                print(f'* Name: {child["name"]}')
        await update.message.reply_html(
            rf'Hi {user.mention_html()}!',
            reply_markup=ForceReply(selective=True),
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        if not self.is_authorized(update.effective_user):
            return
        await update.message.reply_text('Help!')

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        if not self.is_authorized(update.effective_user):
            return
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
