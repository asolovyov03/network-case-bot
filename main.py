import telebot
from config import API_KEY, message_templates
import json
import os

bot = telebot.TeleBot(API_KEY)

def isAdmin(username, json_data):
    for i in range(len(json_data)):
        if username == json_data[i]['username']:
            return True
    return False

@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.from_user.id, message_templates[0])
@bot.message_handler(commands = ['help'])
def help(message):
    with open("admins.json", "r") as json_file:
        json_data = json.load(json_file)
    if isAdmin(message.from_user.username, json_data):
        bot.send_message(message.from_user.id, message_templates[2])
    else:
        bot.send_message(message.from_user.id, message_templates[1])
@bot.message_handler(commands = ['add'])
def add(message):
    bot.send_message(message.from_user.id, message_templates[3])
@bot.message_handler(content_types = ['voice'])
def get_voice(message):
    path = os.getcwd()
    new_path = os.path.join(path, r'voices')
    if message.voice.duration < 120:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        os.chdir(new_path)
        src = str(message.from_user.id) + '_' + str(message.message_id) + '.ogg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        os.chdir(path)
        with open('voices.json', "r") as json_file:
            json_data = json.load(json_file)
        json_data['to_check'].append(str(message.from_user.id) + '_' + str(message.message_id))
        with open('voices.json', 'w') as json_file:
            json.dump(json_data, json_file)
    else:
        bot.send_message(message.from_user.id, message_templates[4])

bot.polling(none_stop=True, interval=0)