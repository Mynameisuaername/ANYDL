from pyrogram import Client, Filters, StopPropagation, InlineKeyboardButton, InlineKeyboardMarkup
import time

bot_start_time = time.time()
bot_uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - bot_start_time))

@Client.on_message(Filters.command(["start"]), group=-2)
async def start(client, message):
    # return
    joinButton = InlineKeyboardMarkup([
        [InlineKeyboardButton("JOIN", url="https://t.me/TGBotsCollection")],
        [InlineKeyboardButton(
            "Try", url="https://t.me/TGBotsCollectionbot")]
    ])
    welcomed = f"Hey <b>{message.from_user.first_name}</b>\nThis is Multipurpose Bot that can perform many functions.\n\n/help for More info \n Bot Uptime : {bot_uptime}"
    await message.reply_text(welcomed, reply_markup=joinButton)
    raise StopPropagation
