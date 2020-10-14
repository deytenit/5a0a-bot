import os
import discord
from github import Github
from discord.ext import commands
from discord import File
import json

bot = commands.Bot(command_prefix = '!') #bot commands prefix
TOKEN = os.getenv("DISCORD_TOKEN")
GTOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GTOKEN)

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
async def algo(ctx, name):
    with open(path + '/cogs/data/cpapi.json', 'r', encoding='utf-8') as f:
        api = json.load(f)
    if not name in api:
        await ctx.send('Could not find file in repo.')
    else:
        repo = g.get_repo('Nartovdima/cp')
        code = repo.get_contents(api[name])
        file = code.decoded_content
        if (len(file.decode('utf-8')) > 1980):
            with open(path + '/cogs/data/code.cpp', 'w') as f:
                f.write(file.decode('utf-8'))
            area = ctx.message.channel
            await ctx.send('**Code is too long! I can only drop the file:**'.format(id = 'text'), file = File(path + '/cogs/data/code.cpp'))
        else: 
            await ctx.send('```cpp\n' + file.decode('utf-8') + '\n```')


@algo.error
async def info_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        repo = g.get_repo('Nartovdima/cp')
        code = repo.get_contents('README.md')
        file = code.decoded_content
        await ctx.send('```md\n' + file.decode('utf-8') + '\n```')

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

if __name__ == "__main__":
    bot.run(TOKEN)
    
# Created by UnknowableShade and Nartov_Dima
