import telebot
import json
import os
import pyqrcode

with open('config.json') as config_file:
    config = json.load(config_file)


token = config['token']
bot=telebot.TeleBot(token)

@bot.message_handler(content_types=['document', 'photo', 'audio', 'video', 'voice'])
def addfile(message: telebot.types.Message):
    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if not os.path.exists(os.path.join("../sercret_files", message.text)):
        os.makedirs(os.path.join("../sercret_files", message.text))
    with open(os.path.join("../sercret_files", message.text, file_name), 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'File saved as {} in {}'.format(file_name, message.text))
    

@bot.message_handler(commands=['qr'])
def create_qr(message: telebot.types.Message):
    qr = pyqrcode.create(os.getenv('CURRENT_IP') + ':5000' + '/qr/' + message.text.split()[1])
    bot.send_photo(message.chat.id, qr.png())