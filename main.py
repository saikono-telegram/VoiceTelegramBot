#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, datetime, requests, os
import speech_recognition as sr
import keyboard as kb
from aiogram import Bot, Dispatcher, executor, types
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot)

async def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result

buttons = types.InlineKeyboardMarkup(row_width=3)
buttons.add(types.InlineKeyboardButton(text='❤️‍🔥 Добавить бота', url="https://telegram.me/SaikoVoice_bot?startgroup=new")) 

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"<b>💙 Привет {message.from_user.full_name}, я бот созданный для преобразования голосовых сообщений в текст, чтобы начать работу со мной пришли мне голосовое сообщение.\n\n🤍 Ты можешь добавить меня в любой чат и голосовые сообщения в них будут автоматически преобразовываться в текст.</b>", parse_mode="html", reply_markup=buttons)

@dp.message_handler(content_types=['voice'])
async def get_audio_messages(message: types.Message):
    msg = await message.answer("🔊 Ожидайте, распознаю...")
    try:
        file_info = await bot.get_file(message.voice.file_id)
        path = file_info.file_path 
        fname = os.path.basename(path) 

        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)

        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        result = await audio_to_text(fname+'.wav')

        if message.forward_from != None:
           await msg.edit_text(f"<b>🤍 От {message.forward_from.full_name}:</b>\n" + format(result), parse_mode="html")
        else:
            await msg.edit_text(f"<b>🤍 От {message.from_user.full_name}:</b>\n" + format(result), parse_mode="html")

    except sr.UnknownValueError as e:
        if message.forward_from != None:
           await msg.edit_text(f"<b>🖤 От {message.forward_from.full_name}:</b>\nНе распознано", parse_mode="html")
        else:
           await msg.edit_text(f"<b>🖤 От {message.from_user.full_name}:</b>\nНе распознано", parse_mode="html")

    finally:
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)