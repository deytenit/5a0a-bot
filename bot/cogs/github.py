#wndrx bot - gitconnecting cog
import discord
from discord.ext import commands
import json
import os
from discord import File
from github import Github

path = os.path.dirname(__file__) + '/data/'

GTOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GTOKEN)

class gitconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'gitconnect cog is active.')

    @commands.command()
    async def algo(self, ctx, name):
        with open(path + '/cpapi.json', 'r', encoding='utf-8') as f:
            api = json.load(f)
        if not name in api:
            await ctx.send('Could not find file in repo.')
        else:
            repo = g.get_repo('Nartovdima/cp')
            code = repo.get_contents(api[name])
            file = code.decoded_content
            if (len(file.decode('utf-8')) > 1980):
                with open(path + '/code.cpp', 'w') as f:
                    f.write(file.decode('utf-8'))
                area = ctx.message.channel
                await ctx.send('**Code is too long! I can only drop the file:**'.format(id = 'text'), file = File(path + '/cogs/data/code.cpp'))
            else: 
                await ctx.send('```cpp\n' + file.decode('utf-8') + '\n```')


    @algo.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            repo = g.get_repo('Nartovdima/cp')
            code = repo.get_contents('README.md')
            file = code.decoded_content
            await ctx.send('```md\n' + file.decode('utf-8') + '\n```')

def setup(bot):
    bot.add_cog(gitconnect(bot))
