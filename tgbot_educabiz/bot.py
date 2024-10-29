#!/usr/bin/env -S python3 -u


import uuid
from functools import lru_cache
from typing import TYPE_CHECKING

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes

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

    def get_chat_ids(self, user: User) -> list['EBClient']:
        return self._chat_ids.get(user.id) or []

    @lru_cache
    def get_child_photo(self, eb: 'EBClient', child_id):
        x = eb.home()
        if child_id in x.children:
            url = x.children[child_id].photo
            photo_bytes = requests.get(url)
            return photo_bytes.content

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        if not self.is_authorized(user):
            return
        ebs = self.get_chat_ids(user)
        for ebi, eb in enumerate(ebs):
            data = eb.school_qrcodeinfo()
            for child in data.child.values():
                assert len(child.presence) == 1
                presence = child.presence[0]
                photo = self.get_child_photo(eb, child.id)
                if presence.id == 'undefined':
                    # undefined -> check in / absent
                    presence_str = '(none)'
                    buttons = [
                        InlineKeyboardButton('check in', callback_data=f'presence {ebi} {child.id} checkin'),
                        InlineKeyboardButton('sick leave', callback_data=f'presence {ebi} {child.id} sickleave'),
                    ]
                elif presence.absent:
                    # absent -> nil
                    presence_str = f'absent ({presence.notes})'
                    buttons = []
                elif not presence.hourOut:
                    # check in -> check out
                    presence_str = f'checked in at {presence.hourIn}'
                    buttons = [
                        InlineKeyboardButton('check out', callback_data=f'presence {ebi} {child.id} checkout'),
                    ]
                else:
                    # check out -> nil
                    presence_str = f'checked in at {presence.hourIn} and out at {presence.hourOut}'
                    buttons = []
                await update.message.reply_photo(
                    photo=photo,
                    caption=rf"""Nome: {child.name}
{presence_str}
                    """,
                    reply_markup=InlineKeyboardMarkup(
                        [buttons, [InlineKeyboardButton('cancel', callback_data='ignore')]]
                    ),
                )

    def setup_app(self) -> Application:
        application = Application.builder().token(self._token).build()
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CallbackQueryHandler(self.handle_buttons))
        return application

    async def handle_buttons(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        await query.answer()
        cmd, *opts = query.data.split(' ', 1)
        if cmd == 'ignore':
            await query.edit_message_reply_markup()
            return
        if cmd == 'presence':
            return await self.handle_buttons_presence(opts, update, context)
        await query.edit_message_caption('Unknown choice...?')

    async def handle_buttons_presence(self, opts: str, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        if opts:
            ebi, child_id, *tail = opts[0].split(' ', 2)
            eb: 'EBClient' = self.get_chat_ids(update.effective_user)[int(ebi)]
            # FIXME: remove print()s over proper checks
            if tail == ['checkin']:
                print(eb.child_check_in(child_id))
                return await query.edit_message_caption('Checked in 📚')
            elif tail == ['checkout']:
                print(eb.child_check_out(child_id))
                return await query.edit_message_caption('Checked out 🏠')
            if tail == ['sickleave']:
                # FIXME: make absent note configurable?
                print(eb.child_absent(child_id, 'Doente'))
                return await query.edit_message_caption('Absent 🤢')
        await query.edit_message_caption('Unknown choice ❓')

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
