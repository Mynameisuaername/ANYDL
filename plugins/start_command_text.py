from pyrogram import Client, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time
bot_start_time = time.time()

''' def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result '''

@Client.on_message(filters.command(["start"]), group=-2)
async def start(client, message):
    bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time)) 
    joinButton = InlineKeyboardMarkup([
        [InlineKeyboardButton("JOIN", url="https://t.me/TGBotsCollection")],
        [InlineKeyboardButton(
            "Try", url="https://t.me/TGBotsCollectionbot")]
    ])
    welcomed = f"Hey <b>{message.from_user.first_name}</b>\nThis is Multipurpose Bot that can perform many functions.\n\n/help for More info \n Bot Uptime : {bot_uptime}"
    await message.reply_text(welcomed, reply_markup=joinButton)
    raise StopPropagation
