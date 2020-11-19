import os
import discord
from discord.ext import commands
import json
import telebot

TOKEN1 = os.getenv("TELEBOT")
bot1 = telebot.TeleBot(TOKEN1)
cnt = 2

@bot1.message_handler(commands=["start"])
def start_chat(message):
    if (message.from_user.username == "alexafonin123"):
        bot1.send_message(message.chat.id, "@gordeve Кто?")
    if (message.from_user.username == "YuriFilatov"):
        bot1.send_message(message.chat.id, "Юра помолчи...", reply_to_message_id=message.message_id)


@bot1.message_handler(content_types=["text"])
def continue_chat(message):
    global cnt
    #print(str(message.from_user.username) + ' ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ': ' + str(message.text))
    if (message.from_user.username == "gordeve"):
        bot1.send_message(message.chat.id, "Неправильно, попробуй еще раз. Попытка: " + str(cnt), reply_to_message_id=message.message_id)
        cnt += 1

bot1.polling(none_stop = True)

bot = commands.Bot(command_prefix = '!') #bot commands prefix
TOKEN = os.getenv("DISCORD_TOKEN")

path = os.path.dirname(__file__)

@bot.event
async def on_ready(): #activates when bot is ready to work
    print(f'--------------------------------')
    print(f'bot is ready') 
    print(f'user name: {bot.user.name}')
    print(f'user id: {bot.user.id}')
    print(f'--------------------------------')

    game = discord.Game("github.com/unknowableshade/5a0a-bot")
    await bot.change_presence(status = discord.Status.idle, activity = game)

 
@bot.command() #loads cogs
async def load_ext(ctx, ext):
    bot.load_extension(f'cogs.{ext}')


@bot.command() #unload cogs
async def unload_ext(ctx, ext):
    bot.unload_extension(f'cogs.{ext}')


for filename in os.listdir(path + '/cogs'): #auto activate all cogs from /cogs directory
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.command()
async def ping(ctx):
    await ctx.send("pong")
    
@bot.command()
async def pong(ctx):
    await ctx.send("ping")

if __name__ == "__main__":
    bot.run(TOKEN)
    
# Created by UnknowableShade and Nartov_Dima
