import telebot
from config import API_KEY
from templates import message_templates
import json
import os
from random import shuffle

ADMINS = []
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.from_user.id, message_templates[0])


@bot.message_handler(commands = ['help'])
def help(message):
    if message.from_user.id in ADMINS:
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


# I'm not sure this handler works, judging by gh readme this should work
@bot.message_handler(commands = ['add_admin'])
def bot_add_admin(message):
    global ADMINS
    if message.from_user.id in ADMINS:
        # message_templates[7] was used here somewhere
        ids = message.text.split()[1:] # "/add_admin 242 4235326" -> ["242", "4235326"]
        try:
            with open('admins.md', 'a') as f:
                for i in ids:
                    ADMINS.append(int(i))
                    f.write(i + "\n")
            success = "ADMIN(S) " + str(ids) + " succesfully added by " + message.from_user.username
            bot.send_message(message.from_user.id, success)
            print(success)
        except:
            bot.send_message(message.from_user.id, "You provided incorrect TELEGRAM ID (should be a number)")
    else:
        bot.send_message(message.from_user.id, message_templates[6])


@bot.message_handler(commands = ['admin_list'])
def get_admin_list(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.from_user.id, str(ADMINS))


@bot.message_handler(commands = ['delete_admin'])
def bot_delete_admin(message):
    global ADMINS
    if message.from_user.id in ADMINS:
        try:
            tg_id = int(message.text.split()[-1])
        except:
            bot.send_message(message.from_user.id, "You provided incorrect TELEGRAM ID (should be a number)")
            return
        if tg_id in ADMINS:
            ADMINS.remove(tg_id)
            with open('admins.md', 'w') as f:
                for admin in ADMINS:
                    f.write(str(admin) + "\n")
            success = "ADMIN " + str(tg_id) + " succesfully deleted by " + message.from_user.username
            bot.send_message(message.from_user.id, success)
            print(success)
        else:
            bot.send_message(message.from_user.id, "There's no such user in admin list (use /admin_list to check the list)")
    else:
        bot.send_message(message.from_user.id, message_templates[6])


with open('admins.md', 'r') as f:
    for line in f:
        try:
            ADMINS.append(int(line))
        except:
            print("problems w/ 'admins.md' file parsing on " + str(line))

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