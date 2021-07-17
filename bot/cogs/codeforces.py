#5a0a bot - codeforces and github cog
import discord
from discord.ext import commands
import requests
import json
import os
import random

PATH = os.path.dirname(__file__) + '/data'

class codeforces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'Codeforces cog is active.')

    @commands.command() #kinda like authentication but actually it's just for solved problems
    async def cf_auth(self, ctx, handle):
        try:
            users = json.loads(requests.get(f'https://codeforces.com/api/user.info?handles={handle}').text)
        except requests.exceptions.HTTPError:
            await ctx.send(f'User {handle} is not found or server is unavailable.')
            return

        with open(PATH + '/users.json', 'r', encoding='utf-8') as file:
            users = json.load(file)

        id = str(ctx.author.id)

        if id not in users:
            users[id] = {}

        users[id]['handle'] = handle

        with open(PATH + '/users.json', 'w', encoding='utf-8') as file:
            json.dump(users, file)        

        applySubmissions(handle) #creating list

        await ctx.send(f'Successfuly authenicated as {handle}. Your submissions has been dumped.')

    @commands.command() #writes down statistics of cf problems also with user stats
    async def cf_database(self, ctx):
        try:
            problems = json.loads(requests.get(f'https://codeforces.com/api/problemset.problems').text)
        except requests.exceptions.HTTPError:
            await ctx.send(f'Codeforces.com is unavailable.')
            return

        cfStats = {}
        userStats = {}

        with open(PATH + '/users.json', 'r', encoding='utf-8') as file:
            users = json.load(file)

        if 'handle' in users[id]:
            handle = users[id]['handle']
            userStats['Amount'] = users[handle]['0']
        else:
            handle = None
            userStats['Amount'] = 0

        cfStats['Amount'] = 0

        for i in range(800, 3501, 100):
            cfStats[i] = 0
            if handle == None:
                userStats[i] = 0
            else:
                userStats[i] = users[handle][str(i)]

        for task in problems['result']['problems']:
            cfStats['Amount'] += 1
            if 'rating' in task:
                cfStats[task['rating']] += 1
        
        anstable = '**Codeforces database cfStatss:**\n' + '```bash\n' + 'Key | Amount | Solved | Overall\n' + '-------------------------------\n'

        for cell in cfStats:
            anstable += f'{cell} | {cfStats[cell]} | {userStats[cell]} | {cfStats[cell] - userStats[cell]}\n'

        anstable += '-------------------------------\n' + '```'

        await ctx.send(anstable)

    @commands.command() #Find random problems on codeforces.com with different filters
    async def cf_task(self, ctx, minr = 1600, maxr = 2600, lastof = 1000, amount = 5, *tags):
        if maxr < minr:
            maxr, minr = minr, maxr

        if (10 > lastof > 7000) or (2 > amount > min(lastof, 10)) or (minr <= maxr < 800) or (maxr >= minr > 3500):
            await ctx.send('Wrong request. Type !help for more info.')
            return

        with open(PATH + '/users.json', 'r', encoding='utf-8') as file:
            users = json.load(file)

        id = str(ctx.author.id)

        if 'handle' not in users[id]:
            await ctx.send('Please authenicate via !cf_auth [Handle].')
            return
        else:
            handle = users[id]['handle']

        applySubmissions(handle, 30)

        tagString = ';'.join(tags)

        try:
            problems = json.loads(requests.get(f'https://codeforces.com/api/problemset.problems?tags={tagString}').text)
        except requests.exceptions.HTTPError:
            await ctx.send('Codeforces.com is unavailable.')

        filteredTasks = []

        for i, task in enumerate(problems['result']['problems']):
            if i == lastof:
                break

            if ('rating' in task) and (minr <= task['rating'] <= maxr):
                if (str(task['contestId']) not in users[handle]['solved']) or (task['index'] not in users[handle]['solved'][str(task['contestId'])]):
                    filteredTasks.append(('https://codeforces.com/contest/' + str(task['contestId']) + '/problem/' + str(task['index']), str(task['rating'])))
        
        for i in range(amount):
            random.seed(None)
            selectedTask = random.choice(filteredTasks)
            filteredTasks.remove(selectedTask)
            await ctx.send(f'You get: {selectedTask[0]} of {selectedTask[1]} rating.')
        
        await ctx.send('Good luck.')


    @commands.command() #That part have direct directory access to following github repo with cool algorithms 
    async def algo_dir(self, ctx, dir = ''):
        try:
            repo = json.loads(requests.get('https://api.github.com/repos/nartovdima/cp/contents' + dir).text)
        except requests.exceptions.HTTPError:
            await ctx.send('Unable to reach destination.')
            return

        if 'name' in repo and repo['type'] == 'file':
            url = repo['download_url']

            fileContent = requests.get(url, allow_redirects=True)
            open(PATH + '/temp.txt', 'wb').write(fileContent.content)
            
            msg = repo['name'] + '\n' + url

            await ctx.send(msg, file=discord.File(PATH + '/temp.txt'))
        else:
            ansdir = '```py\n' + '> cp' + dir + ' $\n'

            for i, file in enumerate(repo):
                type = file['type']
                name = file['name']
                size = file['size']

                ansdir += f'{i} | {type} | {name} | {size} Bytes\n'
            
            ansdir += '```'

            await ctx.send(ansdir)

    @commands.command() #Search in following github repo
    async def algo_search(self, ctx, query = ''):
        try:
            repo = json.loads(requests.get(f'https://api.github.com/search/code?q=repo:nartovdima/cp+filename:{query}').text)
        except requests.exceptions.HTTPError:
            await ctx.send('Nothing was found.')
            return

        if repo['total_count'] == 0:
            await ctx.send('No items were found in repository.')
            return

        if repo['total_count'] == 1:
            try:
                file = json.loads(requests.get(repo['items'][0]['url']).text)
            except requests.exceptions.HTTPError:
                await ctx.send('Unable to reach destination.')
                return

            url = file['download_url']

            fileContent = requests.get(url, allow_redirects=True)
            open(PATH + '/temp.txt', 'wb').write(fileContent.content)
            
            msg = file['name'] + '\n' + url

            await ctx.send(msg, file=discord.File(PATH + '/temp.txt'))
        else:
            ansdir = '```py\n' + '> cp $ find ' + query + '\n'

            for i, file in enumerate(repo['items']):
                name = file['name']
                path = file['path']

                ansdir += f'{i} | {name} | {path}\n'
            
            ansdir += '```'

            await ctx.send(ansdir)


def setup(bot):
    bot.add_cog(codeforces(bot))

def applySubmissions(handle, amount = 0): #Keep in fit user solved problems list
    with open(PATH + '/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)

    if handle not in users:
        users[handle] = {}
        users[handle]['solved'] = {}

        users[handle]['0'] = 0

        for i in range(800, 3501, 100):
            users[handle][str(i)] = 0

    submissions = json.loads(requests.get(f'https://codeforces.com/api/user.status?handle={handle}').text)

    for i, task in enumerate(submissions['result']):
        if i == amount != 0:
            break

        if task['verdict'] == 'OK':
            if str(task['problem']['contestId']) not in users[handle]['solved']:
                users[handle]['solved'][str(task['problem']['contestId'])] = {}

            users[handle]['solved'][str(task['problem']['contestId'])][task['problem']['index']] = 'OK'

            users[handle]['0'] += 1

            if 'rating' in task['problem']:
                users[handle][str(task['problem']['rating'])] += 1

    with open(PATH + '/users.json', 'w', encoding='utf-8') as file:
            json.dump(users, file)
