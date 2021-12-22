'''from pyrogram import Client, filters, StopPropagation
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import psutil
import time
from speedtest import Speedtest


@Client.on_message(filters.command(["speedtest"]) & filters.private)
async def speed(bot, update):
    try:
        spg = await bot.send_message(text=f'Running speedtest....', chat_id=update.chat.id, reply_to_message_id=update.message_id,)
    except Exception as er:
        print(er, 13)
        spg = await bot.send_message(
            text=f'Running speedtest....',
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
        )
    
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = (result['share'])
    try:
        print('Line 28', test)
    except Exception as ere:
        print(ere, '30')
        pass
    string_speed = f'''
<b>Server</b>
<b>Name:</b> <code>{result['server']['name']}</code>
<b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
<b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
    
<b>SpeedTest Results</b>
<b>Upload:</b> <code>{speed_convert(result['upload'] / 8)}</code>
<b>Download:</b>  <code>{speed_convert(result['download'] / 8)}</code>
<b>Ping:</b> <code>{result['ping']} ms</code>
<b>ISP:</b> <code>{result['client']['isp']}</code>
'''

    await spg.delete()
    try:
        print(path, string_speed, type(path), type(string_speed))
    except Exception as pri:
        print(pri)
        
    try:
        await bot.send_photo(
            chat_id=update.chat.id,
            photo=path,
            caption=string_speed,
            parse_mode="HTML",
            reply_to_message_id=update.message_id
        )
    except Exception as cv:
        print("Error 60 ", cv)
        await bot.send_message(
            text=string_speed,
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
        )
        
def speed_convert(size):
    """Hi human, you can't read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "MB/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"        
''' 
