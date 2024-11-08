#!/usr/bin/env -S python3 -u


import logging
import uuid
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field, field_validator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown

if TYPE_CHECKING:
    from educabiz.client import Client as EBClient

logger = logging.getLogger(__name__)


class Bot:
    def __init__(
        self,
        token: str,
        webhook_url: str = None,
        webhook_port: int = None,
        chat_ids: dict[str, list['EBClient']] = None,
        absent_note: str = None,
    ):
        self._token = token
        self._webhook_url = webhook_url
        self._webhook_port = webhook_port
        self._secret_token = uuid.uuid4()
        self._chat_ids = chat_ids
        self._absent_note = absent_note

    def is_authorized(self, user: User):
        return user is not None and user.id in self._chat_ids

    def get_chat_ids(self, user: User) -> list['EBClient']:
        return self._chat_ids.get(user.id) or []

    @lru_cache
    def get_child_photo(self, eb: 'EBClient', child_id):
        x = eb.home()
        if child_id in x.children:
            url = x.children[child_id].photo
            return url

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
                    presence_str = ''
                elif presence.absent:
                    # absent -> nil
                    presence_str = '🤢 Absent'
                    if presence.notes:
                        presence_str += f' - {presence.notes}'
                elif not presence.hourOut:
                    action_str = 'in'
                    # check in -> check out
                    presence_str = f'🛬 Checked in at {presence.hourIn}'
                else:
                    # check out -> nil
                    presence_str = f'🛬 Check in: {presence.hourIn}\n🚶‍♂️ Check out: {presence.hourOut}'

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

                message = f"""\
*Nome*: {child.name}
{escape_markdown(presence_str, version=2)}"""

                if photo is None:
                    return await update.message.reply_markdown_v2(
                        message,
                        reply_markup=reply_markup,
                    )
                else:
                    await update.message.reply_photo(
                        photo=photo, caption=message, reply_markup=reply_markup, parse_mode='MarkdownV2'
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
            ebi, child_id, tail = opts[0].split(' ', 2)
            eb: 'EBClient' = self.get_chat_ids(update.effective_user)[int(ebi)]
            if tail == 'checkin':
                r = eb.child_check_in(child_id)
                logger.debug('CHECKIN RESPONSE: %s', r)
                cd = PresenceCheck.model_validate(r)
                logger.info(f'{update.effective_user.id} checked IN {child_id}')
                return await query.edit_message_caption(f'🛬 Checked in at {cd.entry_in.time}')
            elif tail == 'checkout':
                r = eb.child_check_out(child_id)
                logger.debug('CHECKOUT RESPONSE: %s', r)
                cd = PresenceCheck.model_validate(r)
                logger.info(f'{update.effective_user.id} checked OUT {child_id}')
                return await query.edit_message_caption(
                    f'🛬 Check in: {cd.entry_in.time}\n🚶‍♂️ Check out: {cd.entry_out.time}'
                )
            if tail == 'sickleave':
                # FIXME: update once a sample is available
                r = eb.child_absent(child_id, self._absent_note or '')
                logger.debug('ABSENT RESPONSE: %s', r)
                cd = PresenceCheck.model_validate(r)
                logger.info(f'{update.effective_user.id} marked {child_id} as absent')
                return await query.edit_message_caption('🤢 Absent')
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


class PresenceCheckEntry(BaseModel):
    """
    TODO: move this to python-educabiz instead!

    {'time': '09:35', 'hour': 9, 'minutes': 35, 'fetcher': 'Pai'}
    """

    model_config = {'extra': 'allow'}

    time: str = None

    @field_validator('time')
    def parse_hours(cls, value):
        if value == '--:--':
            return ''
        return value


class PresenceCheck(BaseModel):
    """
    TODO: move this to python-educabiz instead!

    Examples of responses

    Check out:
    {'isAbsent': False, 'hasIn': True, 'hasOut': True, 'hasNotes': False, 'isLate': True, 'late': '09:11', 'isEarly': False, 'early': '00:00', 'islatepenaltyin': False, 'islatepenaltyout': False, 'in': {'time': '09:35', 'hour': 9, 'minutes': 35, 'fetcher': 'Pai'}, 'out': {'time': '17:11', 'hour': 17, 'minutes': 11, 'fetcher': 'Mãe'}}"
    Check in:
    {'isAbsent': False, 'hasIn': True, 'hasOut': False, 'hasNotes': False, 'isLate': False, 'isEarly': True, 'early': '00:00', 'islatepenaltyin': False, 'islatepenaltyout': False, 'in': {'time': '09:52', 'hour': 9, 'minutes': 52, 'fetcher': 'Pai'}, 'out': {'time': '--:--', 'hour': 0, 'minutes': 0, 'fetcher': ''}}"
    """

    model_config = {'extra': 'allow'}

    isAbsent: bool = False
    hasIn: bool = False
    hasOut: bool = False
    entry_in: Optional[PresenceCheckEntry] = Field(default=None, alias='in')
    entry_out: Optional[PresenceCheckEntry] = Field(default=None, alias='out')
