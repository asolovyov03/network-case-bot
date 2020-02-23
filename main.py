import telebot
from config import API_KEY
from templates import message_templates
import json
import os
from random import shuffle

bot = telebot.TeleBot(API_KEY)

def isAdmin(username, message):
    with open("admins.json", "r") as json_file:
        json_data = json.load(json_file)
    for i in range(len(json_data)):
        if username == json_data[i]['username']:
            if 'id' not in json_data[i]:
                json_data[i].update({'id': message.from_user.id})
                with open('admins.json', 'w') as json_file:
                    json.dump(json_data, json_file)
            return True
    return False

@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.from_user.id, message_templates[0])
@bot.message_handler(commands = ['help'])
def help(message):
    if isAdmin(message.from_user.username, message):
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
        src = 'v' + str(message.from_user.id) + '_' + str(message.message_id) + '.ogg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        os.chdir(path)
        with open('voices.json', "r") as json_file:
            json_data = json.load(json_file)
        json_data['to_check'].append(str(message.from_user.id) + '_' + str(message.message_id))
        with open('voices.json', 'w') as json_file:
            json.dump(json_data, json_file)
        bot.send_message(message.from_user.id, message_templates[5])
    else:
        bot.send_message(message.from_user.id, message_templates[4])

@bot.message_handler(commands = ['add_admin'])
def bot_add_admin(message):
    if isAdmin(message.from_user.username, message):
        msg = bot.send_message(message.from_user.id, message_templates[7])
        bot.register_next_step_handler(msg, add_admin)
    else:
        bot.send_message(message.from_user.id, message_templates[6])

def add_admin(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, message_templates[8])
    else:
        admins = message.text.split()
        message_template = '''Вот список тех, кого вы назначили админом:
'''
        for i in range(len(admins)):
            if admins[i][0] == '@':
                admins[i] = admins[i][1:len(admins[i])]
            message_template += "@" + admins[i] + '\n'
        with open('admins.json', 'r') as json_file:
            json_data = json.load(json_file)
        for i in range(len(admins)):
            json_data.append({'username':admins[i]})
        with open('admins.json', 'w') as json_file:
            json.dump(json_data, json_file)
        bot.send_message(message.from_user.id, message_template)

@bot.message_handler(commands = ['delete_admin'])
def bot_delete_admin(message):
    if isAdmin(message.from_user.username, message):
        with open('admins.json', 'r') as json_file:
            json_data = json.load(json_file)
        message_template = 'Вот список действующих админов:\n'
        for i in range(len(json_data)):
            message_template += '@' + json_data[i]['username'] + ' - /' + str(i + 1) + '\n'
        message_template += '''Выберите того, кого хотите удалить (чтобы удалить нескольких, вызовите /delete_admin несколько раз)
Для отмены действия используйте /cancel'''
        msg = bot.send_message(message.from_user.id, message_template)
        bot.register_next_step_handler(msg, delete_admin)
    else:
        bot.send_message(message.from_user.id, message_templates[6])

def delete_admin(message):
    with open('admins.json', 'r') as json_file:
        json_data = json.load(json_file)
    if message.text == '/cancel':
        bot.send_message(message.from_user.id, message_templates[8])
    else:
        if (message.text[0] == "/") and (message.text[1:len(message.text)].isdigit()):
            if (int(message.text[1:len(message.text)]) <= len(json_data)):
                deleted_username = json_data.pop(int(message.text[1:len(message.text)]) - 1)['username']
                with open('admins.json', 'w') as json_file:
                    json.dump(json_data, json_file)
                bot.send_message(message.from_user.id, '@' + deleted_username + ' больше не админ')
            else:
                bot.send_message(message.from_user.id, message_templates[10])
        else:
            bot.send_message(message.from_user.id, message_templates[9])

@bot.message_handler(commands = ['listen'])
def listen(message):
    with open('voices.json', 'r') as json_file:
        json_data = json.load(json_file)
    if len(json_data['checked']) > 0:
        shuffle(json_data['checked'])
        audio_id = json_data['checked'][0]
        print(audio_id)
        path = os.getcwd()
        new_path = os.path.join(path, r'voices')
        os.chdir(new_path)
        bot.send_voice(message.from_user.id, open(audio_id + '.ogg', 'rb'))
        os.chdir(path)
    else:
        bot.send_message(message.from_user.id, message_templates[11])

bot.polling(none_stop=True, interval=0)