import telebot
import json
import os
import pyqrcode

with open('./src/config.json') as config_file:
    config = json.load(config_file)


token = config['token']
bot=telebot.TeleBot(token)

def process_file_step(message: telebot.types.Message, folder_name, file_name):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

    print("./secret_files", folder_name, file_name, folder_name, "\n")

    if not os.path.exists(os.path.join("./secret_files", folder_name)):
        os.makedirs(os.path.join("./secret_files", folder_name))
    with open(os.path.join("./secret_files", folder_name, file_name), 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'File saved as {} in {}'.format(file_name, folder_name))

def process_name_step(message: telebot.types.Message, folder_name):
    bot.reply_to(message, "Отправьте файл:")
    bot.register_next_step_handler(message, process_file_step, folder_name, message.text)

def process_folder_name_step(message: telebot.types.Message):
    bot.reply_to(message, "Введите название файла:")
    bot.register_next_step_handler(message, process_name_step, message.text)

@bot.message_handler(commands=['add'])
def addfile(message: telebot.types.Message):
    bot.reply_to(message, "Введите название статьи:")
    bot.register_next_step_handler(message, process_folder_name_step)



@bot.message_handler(commands=['qr'])
def create_qr(message: telebot.types.Message):
    qr = pyqrcode.create(os.getenv('CURRENT_IP') + ':5000' + '/qr/' + message.folder_name.split()[1])
    qr_file_path = os.path.join("../qr_codes", str(message.folder_name.split()[1:]) + '.png')
    if not os.path.exists("./qr_codes"):
        os.makedirs("./qr_codes")
    qr.png(qr_file_path, scale=8)
    with open(qr_file_path, 'rb') as qr_file:
        bot.send_photo(message.chat.id, qr_file)

bot.infinity_polling()