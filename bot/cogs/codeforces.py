#wndrx bot - codeforces cog
import discord
from discord.ext import commands
import json
import os
import urllib
import random
from urllib.request import urlopen

path = os.path.dirname(__file__) + '/data'

class codeforces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'Codeforces cog is active.')

    @commands.command()
    async def cf_auth(self, ctx, handle):
        try:
            user = json.loads(urlopen(f'https://codeforces.com/api/user.info?handles={handle}').read())
            with open(f'{path}/users.json', 'r', encoding='utf-8') as file:
                users = json.load(file)

            id = str(ctx.author.id)
            if id not in users:
                users[id] = {}

            users[id]['handle'] = handle

            with open(f'{path}/users.json', 'w', encoding='utf-8') as file:
                json.dump(users, file)

            await ctx.send(f'Successfuly authenicated as {handle}.')

        except urllib.error.HTTPError:
            await ctx.send(f'User {handle} is not found or server is unavailable.')

    @commands.command()
    async def cf_database(self, ctx):
        try:
            problems = json.loads(urlopen(f'https://codeforces.com/api/problemset.problems').read())

            statistic = {'Amount': 0}

            for i in range(800, 3501, 100):
                statistic[i] = 0

            for task in problems['result']['problems']:
                statistic['Amount'] += 1
                if 'rating' in task:
                    statistic[task['rating']] += 1
            
            table = f'**Codeforces database statistics:**\n\n```bash\nKey     Amount\n---------------\n'

            for cell in statistic:
                table += f'{cell} | {statistic[cell]}\n'

            table += '```'

            await ctx.send(table)

        except urllib.error.HTTPError:
            await ctx.send(f'Server is unavailable.')

    @commands.command()
    async def cf_task(self, ctx, minr = 1600, maxr = 2600, amount = 1000, *tags):
        stroftags = ';'.join(tags)
        try:
            problems = json.loads(urlopen(f'https://codeforces.com/api/problemset.problems?tags={stroftags}').read())

            sortedtasks = []

            for i, task in enumerate(problems['result']['problems']):
                if ('rating' in task) and (minr <= int(task['rating']) <= maxr):
                    sortedtasks.append(('https://codeforces.com/contest/' + str(task['contestId']) + '/problem/' + str(task['index']), str(task['rating'])))
                if i == amount:
                    break
            
            

            selectedtask = random.choice(sortedtasks)

            await ctx.send(f'You get: {selectedtask[0]} of {selectedtask[1]} rating.')

        except urllib.error.HTTPError:
            await ctx.send(f'Server is unavailable.')

def setup(bot):
    bot.add_cog(codeforces(bot))
