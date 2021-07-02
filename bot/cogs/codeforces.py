#wndrx bot - codeforces cog
import discord
from discord.ext import commands
import requests
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

            users[users[id]['handle']] = {}
            users[users[id]['handle']]['solved'] = {}

            for i in range(800, 3501, 100):
                users[users[id]['handle']][i] = 0

            users[users[id]['handle']][0] = 0

            submissions = json.loads(urlopen('https://codeforces.com/api/user.status?handle=' + users[id]['handle']).read())

            for task in submissions['result']:
                if task['verdict'] == 'OK':
                    if task['problem']['contestId'] not in users[users[id]['handle']]['solved']:
                        users[users[id]['handle']]['solved'][task['problem']['contestId']] = {}
                    users[users[id]['handle']]['solved'][task['problem']['contestId']][task['problem']['index']] = 'OK'
                    if 'rating' in task['problem']:
                        users[users[id]['handle']][task['problem']['rating']] += 1
                    users[users[id]['handle']][0] += 1
                print(f'{id} dumped stats.')

            with open(f'{path}/users.json', 'w', encoding='utf-8') as file:
                json.dump(users, file)

            await ctx.send(f'Successfuly authenicated as {handle}. Submissions have been dumped')

        except urllib.error.HTTPError:
            await ctx.send(f'User {handle} is not found or server is unavailable.')

    @commands.command()
    async def cf_database(self, ctx):
        with open(f'{path}/users.json', 'r', encoding='utf-8') as file:
                users = json.load(file)
        id = str(ctx.author.id)
        try:
            problems = json.loads(urlopen(f'https://codeforces.com/api/problemset.problems').read())

            statistic = {'Amount': 0}
            antistatistic = {}

            antistatistic['Amount'] = users[users[id]['handle']]['0']

            for i in range(800, 3501, 100):
                statistic[i] = 0
                if 'handle' not in users[id]:
                    antistatistic[i] = 0
                else:
                    antistatistic[i] = users[users[id]['handle']][str(i)]

            for task in problems['result']['problems']:
                statistic['Amount'] += 1
                if 'rating' in task:
                    statistic[task['rating']] += 1
            
            table = f'**Codeforces database statistics:**\n\n```bash\nKey     Amount     Solved     Overall\n-------------------------------------\n'

            for cell in statistic:
                table += f'{cell} | {statistic[cell]} | {antistatistic[cell]} | {statistic[cell] - antistatistic[cell]}\n'

            table += '```'

            await ctx.send(table)

        except urllib.error.HTTPError:
            await ctx.send(f'Server is unavailable.')

    @commands.command()
    async def cf_task(self, ctx, minr = 1600, maxr = 2600, indexcnt = 1000, *tags):
        with open(f'{path}/users.json', 'r', encoding='utf-8') as file:
            users = json.load(file)
        id = str(ctx.author.id)
        if 'handle' not in users[id]:
            await ctx.send('Authenicate.')
            pass

        if maxr < minr:
            maxr, minr = minr, maxr
        if (indexcnt < 10) or (minr <= maxr < 800) or (maxr >= minr > 3500):
            await ctx.send('Wrong request.')
            pass
        stroftags = ';'.join(tags)
        try:
            problems = json.loads(urlopen(f'https://codeforces.com/api/problemset.problems?tags={stroftags}').read())

            sortedtasks = []

            print(len(problems['result']['problems']))

            submissions = json.loads(urlopen('https://codeforces.com/api/user.status?count=30&handle=' + users[id]['handle']).read())

            for task in submissions['result']:
                if task['verdict'] == 'OK':
                    users[users[id]['handle']]['solved'][str(task['problem']['contestId'])][task['problem']['index']] = 'OK'

            with open(f'{path}/users.json', 'w', encoding='utf-8') as file:
                json.dump(users, file)

            for i, task in enumerate(problems['result']['problems']):
                if ('rating' in task) and (minr <= int(task['rating']) <= maxr):
                    if (str(task['contestId']) not in users[users[id]['handle']]['solved']) or (str(task['contestId']) in users[users[id]['handle']]['solved']) and (task['index'] not in users[users[id]['handle']]['solved'][str(task['contestId'])]):
                        sortedtasks.append(('https://codeforces.com/contest/' + str(task['contestId']) + '/problem/' + str(task['index']), str(task['rating'])))
                if i == indexcnt:
                    break
                    
            
            random.seed(None)
            selectedtask = random.choice(sortedtasks)

            await ctx.send(f'You get: {selectedtask[0]} of {selectedtask[1]} rating.')

        except urllib.error.HTTPError:
            await ctx.send(f'Server is unavailable.')

    @commands.command()
    async def cf_tasks(self, ctx, minr = 1600, maxr = 2600, indexcnt = 1000, amount = 5, *tags):
        if maxr < minr:
            maxr, minr = minr, maxr
        if (indexcnt < 10) or (amount < 2) or (minr <= maxr < 800) or (maxr >= minr > 3500):
            await ctx.send('Wrong request.')
            pass
        stroftags = ';'.join(tags)
        try:
            problems = json.loads(urlopen(f'https://codeforces.com/api/problemset.problems?tags={stroftags}').read())

            sortedtasks = []

            for i, task in enumerate(problems['result']['problems']):
                if ('rating' in task) and (minr <= int(task['rating']) <= maxr):
                    sortedtasks.append(('https://codeforces.com/contest/' + str(task['contestId']) + '/problem/' + str(task['index']), str(task['rating'])))
                if i == indexcnt:
                    break
            
            for i in range(amount):
                random.seed(None)
                selectedtask = random.choice(sortedtasks)
                sortedtasks.remove(selectedtask)
                await ctx.send(f'You get: {selectedtask[0]} of {selectedtask[1]} rating.')

        except urllib.error.HTTPError:
            await ctx.send(f'Server is unavailable.')


    @commands.command()
    async def algo_dir(self, ctx, dir = ''):
        try:
            repo = json.loads(urlopen('https://api.github.com/repos/nartovdima/cp/contents' + dir).read())
            if 'name' in repo and repo['type'] == 'file':
                url = repo['download_url']
                file = requests.get(url, allow_redirects=True)
                open(f'{path}/temp.txt', 'wb').write(file.content)
                await ctx.send(url, file=discord.File(f'{path}/temp.txt'))
            else:
                answer = f'cp{dir} contents.\n```bash\n'

                for i, file in enumerate(repo):
                    type = file['type']
                    name = file['name']
                    size = file['size']

                    answer += f'{i} | {type} | {name} | {size} Bytes\n'
                
                answer += '```'

                print(answer)
                await ctx.send(answer)
        except urllib.error.HTTPError:
            await ctx.send(f'Unable to reach destination.')

def setup(bot):
    bot.add_cog(codeforces(bot))
