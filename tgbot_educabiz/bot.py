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
                action_str = None
                if presence.id == 'undefined':
                    # undefined -> check in / absent
                    action_str = 'none'
                    presence_str = '(none)'

                elif presence.absent:
                    # absent -> nil
                    presence_str = f'absent ({presence.notes})'
                elif not presence.hourOut:
                    action_str = 'in'
                    # check in -> check out
                    presence_str = f'checked in at {presence.hourIn}'
                else:
                    # check out -> nil
                    presence_str = f'checked in at {presence.hourIn} and out at {presence.hourOut}'

                if action_str:
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    '📋 Actions', callback_data=f'actions {ebi} {child.id} {action_str}'
                                ),
                            ]
                        ]
                    )
                else:
                    reply_markup = None

                await update.message.reply_photo(
                    photo=photo,
                    caption=rf"""Nome: {child.name}
{presence_str}
                    """,
                    reply_markup=reply_markup,
                )

    def setup_app(self) -> Application:
        application = Application.builder().token(self._token).post_init(self.post_init).build()
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CallbackQueryHandler(self.handle_buttons))
        return application

    async def post_init(self, application: Application) -> None:
        await application.bot.set_my_commands([('start', 'Show kids')])

    async def handle_buttons(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        await query.answer()
        cmd, *opts = query.data.split(' ', 1)
        if cmd == 'ignore':
            return await query.edit_message_reply_markup()
        if cmd == 'actions':
            return await self.handle_buttons_actions(opts, update, context)
        if cmd == 'presence':
            return await self.handle_buttons_presence(opts, update, context)
        return await query.edit_message_caption('Unknown choice...?')

    async def handle_buttons_actions(self, opts: str, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        if opts:
            ebi, child_id, action = opts[0].split(' ', 2)
            if action == 'none':
                return await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('🛬 Check in', callback_data=f'presence {ebi} {child_id} checkin'),
                                InlineKeyboardButton(
                                    '🤢 Sick leave', callback_data=f'presence {ebi} {child_id} sickleave'
                                ),
                            ],
                            [InlineKeyboardButton('✖️ Dismiss', callback_data='ignore')],
                        ]
                    )
                )
            if action == 'in':
                return await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    '🚶‍♂️Check out', callback_data=f'presence {ebi} {child_id} checkout'
                                ),
                            ],
                            [InlineKeyboardButton('✖️ Dismiss', callback_data='ignore')],
                        ]
                    )
                )

        await query.edit_message_caption('Unknown choice ❓')

    async def handle_buttons_presence(self, opts: str, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        if opts:
            ebi, child_id, *tail = opts[0].split(' ', 2)
            eb: 'EBClient' = self.get_chat_ids(update.effective_user)[int(ebi)]
            # FIXME: remove print()s over proper checks
            if tail == ['checkin']:
                print(eb.child_check_in(child_id))
                print(f'{update.effective_user.id} checked IN {child_id}')
                return await query.edit_message_caption('Checked in 📚')
            elif tail == ['checkout']:
                print(eb.child_check_out(child_id))
                print(f'{update.effective_user.id} checked OUT {child_id}')
                return await query.edit_message_caption('Checked out 🏠')
            if tail == ['sickleave']:
                # FIXME: make absent note configurable?
                print(eb.child_absent(child_id, 'Doente'))
                print(f'{update.effective_user.id} marked {child_id} as absent')
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
