#!/usr/bin/python

import telebot
import json
import os
import pyqrcode
import hashlib
import requests
import pandas as pd

current_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(current_file_path, 'src/config.json')) as config_file:
    config = json.load(config_file)


token = config['token']
bot=telebot.TeleBot(token)

def process_file_step(message: telebot.types.Message, folder_name):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # file_name = message.photo[-1].file_id[10:30]
        file_name = str(hashlib.sha1(message.photo[-1].file_id.encode("utf-8")).hexdigest()) 

    if not os.path.exists(os.path.join(current_file_path, "secret_files", folder_name)):
        os.makedirs(os.path.join(current_file_path, "secret_files", folder_name))
    with open(os.path.join(current_file_path, "secret_files", folder_name, file_name), 'wb') as new_file:
        new_file.write(downloaded_file)
    file_name_button = telebot.types.InlineKeyboardButton(text='Изменить имя файла', callback_data=f"{folder_name}_-_{file_name}")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(file_name_button)
    bot.send_message(message.chat.id, 'File saved as {} in {}. \nYou really need to change name if it is pic.'.format(file_name, folder_name), reply_markup=keyboard)

def process_name_step(message: telebot.types.Message):
    if " " in message.text:
        bot.reply_to(message, "Название статьи не должно содержать пробелов")
        bot.register_next_step_handler(message, process_name_step)
    bot.reply_to(message, "Отправьте файл:")
    bot.register_next_step_handler(message, process_file_step, message.text)

def change_name_step(message: telebot.types.Message, folder_name, file_name):
    os.rename(os.path.join(current_file_path, "secret_files", folder_name, file_name), os.path.join(current_file_path, "secret_files", folder_name, message.text))
    file_name_button = telebot.types.InlineKeyboardButton(text='Изменить имя файла', callback_data=f"{folder_name}_-_{message.text}")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(file_name_button)
    bot.reply_to(message, "Имя файла изменено на {}".format(message.text), reply_markup=keyboard)

@bot.message_handler(commands=['add_secret'])
def addfile(message: telebot.types.Message):
    bot.reply_to(message, "Введите название статьи:")
    bot.register_next_step_handler(message, process_name_step)



@bot.message_handler(commands=['qr'])
def create_qr(message: telebot.types.Message):
    qr = pyqrcode.create(os.getenv('CURRENT_IP') + ':5000' + '/qr/' + message.text.split()[1])
    qr_file_path = os.path.join(current_file_path, "qr_codes", str(message.text.split()[1:]) + '.png')
    if not os.path.exists(os.path.join(current_file_path, "qr_codes")):
        os.makedirs(os.path.join(current_file_path, "qr_codes"))
    qr.png(qr_file_path, scale=8)
    with open(qr_file_path, 'rb') as qr_file:
        bot.send_photo(message.chat.id, qr_file)

def process_subfolder(message: telebot.types.Message, folder_name):
    with open(os.path.join(current_file_path, 'secret_files', folder_name, "subfolder"), "w") as subfolder_file:
        subfolder_file.write(message.text)
    bot.reply_to(message, "Подпапка добавлена")

def get_folder(message: telebot.types.Message):
    bot.reply_to(message, "Введите полную подпапку:")
    bot.register_next_step_handler(message, process_subfolder, message.text)

@bot.message_handler(commands=['subfolders'])
def add_subfolder(message: telebot.types.Message):
    bot.reply_to(message, "Введите название статьи:")
    bot.register_next_step_handler(message, get_folder)

def get_to_publish(message: telebot.types.Message):
    resp = requests.get('http://127.0.0.1:5000/qr/' + message.text)
    if resp.status_code == 200:
        bot.reply_to(message, "Статья опубликована")
    else:
        bot.reply_to(message, "Что-то пошло не так")

@bot.message_handler(commands=['publish'])
def add_subfolder(message: telebot.types.Message):
    bot.reply_to(message, "Введите название статьи:")
    bot.register_next_step_handler(message, get_to_publish)


@bot.callback_query_handler(func=lambda call: True)
def process_folder_name_step(call: telebot.types.CallbackQuery):
    folder, file = call.data.split('_-_')
    bot.send_message(call.message.chat.id, "Введите новое имя файла:")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.register_next_step_handler(call.message, change_name_step, folder, file)


def process_players(message: telebot.types.Message):
    if message.document:
        file_info = bot.get_file('players_list.xlsx')
        downloaded_file = bot.download_file(file_info.file_path)
    else:
        bot.reply_to(message, "Ашипка")
        return
    with open(os.path.join(current_file_path, 'players_list.xlsx'), 'wb') as new_file:
        new_file.write(downloaded_file)

    players = pd.read_excel('players_list.xlsx')
    for player in players:
        print(player)
        bot.send_message(message.chat.id, f"Игрок {player} добавлен")
        


@bot.message_handler(commands=["add_players"])
def add_players(message: telebot.types.Message):
    bot.reply_to(message, "Отправьте файл. Файл отправляется строго в xlsx формате, иначе ничего не сработает:")
    bot.register_next_step_handler(message, process_players)


@bot.message_handler(commands=['help'])
def send_help(message: telebot.types.Message):
    help_text = (
        "/add_secret - Добавить секретный файл\n"
        "/qr <text> - Создать QR-код\n"
        "/subfolders - Добавить подпапку\n"
        "/publish - Опубликовать статью\n"
        "/help - Показать это сообщение"
    )
    bot.reply_to(message, help_text)

bot.infinity_polling()