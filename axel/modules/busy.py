from typing import Optional

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from axel import dispatcher
from axel.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from axel.modules.sql import busy_sql as sql
from axel.modules.users import get_user_id

BUSY_GROUP = 7
BUSY_REPLY_GROUP = 8


@run_async
def busy(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2:
        reason = args[1]
    else:
        reason = ""

    sql.set_busy(update.effective_user.id, reason)
    update.effective_message.reply_text("{} is now BUSY! because he is {}".format(update.effective_user.first_name, reason))


@run_async
def no_longer_busy(bot: Bot, update: Update):
    user = update.effective_user  # type: Optional[User]

    if not user:  # ignore channels
        return

    res = sql.rm_busy(user.id)
    if res:
        update.effective_message.reply_text("{} is no longer BUSY!".format(update.effective_user.first_name))


@run_async
def reply_busy(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
    if message.entities and entities:
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(message.text[ent.offset:ent.offset + ent.length])
                if not user_id:
                    # Should never happen, since for a user to become BUSY they must have spoken. Maybe changed username?
                    return
                chat = bot.get_chat(user_id)
                fst_name = chat.first_name

            else:
                return

            if sql.is_busy(user_id):
                valid, reason = sql.check_busy_status(user_id)
                if valid:
                    if not reason:
                        res = "{} is BUSY!".format(fst_name)
                    else:
                        res = "{} is BUSY because he is {}".format(fst_name, reason)
                    message.reply_text(res)


def __gdpr__(user_id):
    sql.rm_busy(user_id)


__help__ = """
 - /busy <reason>: mark yourself as BUSY.
 - brb <reason>: same as the busy command - but not a command.

When marked as BUSY, any mentions will be replied to with a message to say you're not available!
"""

__mod_name__ = "Busy"

BUSY_HANDLER = DisableAbleCommandHandler("busy", busy)
BUSY_REGEX_HANDLER = DisableAbleRegexHandler("(?i)brb", busy, friendly="busy")
NO_BUSY_HANDLER = MessageHandler(Filters.all & Filters.group, no_longer_busy)
BUSY_REPLY_HANDLER = MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION),
                                   reply_busy)

dispatcher.add_handler(BUSY_HANDLER, BUSY_GROUP)
dispatcher.add_handler(BUSY_REGEX_HANDLER, BUSY_GROUP)
dispatcher.add_handler(NO_BUSY_HANDLER, BUSY_GROUP)
dispatcher.add_handler(BUSY_REPLY_HANDLER, BUSY_REPLY_GROUP)
