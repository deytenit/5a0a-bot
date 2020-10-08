#wndrx bot - leveling cog
import discord
from discord.ext import commands
import json
import os

path = os.path.dirname(__file__) + '/data/'

class level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'Level cog is active.')

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.content.startswith('-') and not msg.content.startswith('!') and not msg.author.bot:
            usr = str(msg.author.id)
            with open(path + 'users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)

            if usr not in users:
                users[usr] = {}
                users[usr]['karma'] = 1
            else:
                users[usr]['karma'] = str(int(users[usr]['karma']) + 1)

            with open(path + 'users.json', 'w') as f:
                json.dump(users, f)

    @commands.command()
    async def karma(self, ctx, temp):
        usr = str(temp.id)
        with open(path + 'users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)

        if usr not in users:
            users[usr] = {}
            users[usr]['karma'] = 0
        await ctx.send(f'**{temp} karma is ' + str(users[usr]['karma']) + '**')

        with open(path + 'users.json', 'w') as f:
            json.dump(users, f)

    @karma.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'I could not find that member...')

        if isinstance(error, commands.MissingRequiredArgument):
            usr = str(ctx.message.author.id)
            with open(path + 'users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            if usr not in users:
                users[usr] = {}
                users[usr]['karma'] = 0
            await ctx.send(f'**Your karma is ' + str(users[usr]['karma']) + '**')
            with open(path + 'users.json', 'w') as f:
                json.dump(users, f)


    @commands.command() #rating of people with most karma on server
    async def krating(self, ctx):
        with open(path + 'users.json', 'r') as f:
            users = json.load(f)

        a = []
        s = f'```cs\n'

        for usr in users:
            a.append((str(self.bot.get_user(int(usr))), int(users[usr]['karma'])))
        a.sort(reverse = True, key = cmp)

        for i in range(len(a)):
            s += f'#{str(i + 1)} {a[i][0]} = {str(a[i][1])} karma\n'
        s += f'```'
        if (len(a) == 0):
            await ctx.send(f'**Nobody on server have karma...**')
        else:
            await ctx.send(s) 
            
    @commands.command()
    async def flip(ctx, self, side, bet=100):
        usr = str(ctx.message.author.id)
        side = side.lower()
        with open(path + 'users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
          
        if not usr in users:
            await ctx.send('You do not have any karma.')
        else:
            tmp = random.randint(0, 7)
            if tmp < 4:
                if side == 'tails':
                    users[usr]['karma'] = str(round(int(users[usr]['karma']) * 1.25))
                    await ctx.send('Tails - You win!')
                else:
                    await ctx.send('Heads - You lose.')
                    
            if tmp > 4:
                if side == 'heads':
                    users[usr]['karma'] = str(round(int(users[usr]['karma']) * 1.25))
                    await ctx.send('Heads - You win!')
                else:
                    await ctx.send('Tails - You lose.')
            
            if tmp == 4:
                if side == 'side':
                    users[usr]['karma'] = str(round(int(users[usr]['karma']) * 1.75))
                    await ctx.send('Side - Jackpot!')
                else:
                    await ctx.send('Not side - You lose.')

def cmp(obj): #comporator for rating sorting
    return obj[1]

def setup(bot):
    bot.add_cog(level(bot))
