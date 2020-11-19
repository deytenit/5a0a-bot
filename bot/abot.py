import telebot
import os

TOKEN = os.getenv("TELEBOT")
bot = telebot.TeleBot(TOKEN)
cnt = 2

@bot.message_handler(commands=["start"])
def start_chat(message):
    bot.send_message(message.chat.id, "@gordeve Кто?")
    if (message.from_user.username == "YuriFilatov"):
        bot.send_message(message.chat.id, "Юра помолчи...", reply_to_message_id=message.message_id)


@bot.message_handler(content_types=["text"])
def continue_chat(message):
    global cnt
    #print(str(message.from_user.username) + ' ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))
    if (message.from_user.username == "gordeve"):
        bot.send_message(message.chat.id, "Неправильно, попробуй еще раз. Попытка: " + str(cnt), reply_to_message_id=message.message_id)
        cnt += 1

bot.polling(none_stop = True)