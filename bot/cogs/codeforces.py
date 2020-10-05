#wndrx bot - codeforces cog
import discord
from discord.ext import commands
import json
import os
import random
from urllib.request import urlopen

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\data'

os.chdir(path)

class codeforces(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'Codeforces cog is active.')


    @commands.command() #update cf task db
    async def update(self, ctx):
        url = 'https://codeforces.com/api/problemset.problems'
        json_url = urlopen(url)
        probs = json.loads(json_url.read())

        with open('problems.json', 'w') as f:
            json.dump(probs, f)

        await ctx.send(f'Codeforces db updated successfully.')


    @commands.command() #send url to random cf problem in specific dificulty range
    async def sproblem(self, ctx, minr = 1700, maxr = 2200):
        with open('problems.json', encoding = 'utf-8') as f:
            probs = json.load(f)

        ps = []

        for prb in probs['result']['problems']:
            if ('rating' in prb) and (prb['rating'] >= minr) and (prb['rating'] <= maxr):
                ps.append('https://codeforces.com/problemset/problem/' + str(prb['contestId']) + '/' + str(prb['index']))

        await ctx.send(random.choice(ps))


    @commands.command() #creating mashup of random cf problems in specific dificulty range
    async def genmash(self, ctx, minr = 1700, maxr = 2200, cnt = 4, mod = '-ns'):
        with open('problems.json', encoding = 'utf-8') as f:
            probs = json.load(f)

        ps = []
        pss = []
        s = f'\n'

        for prb in probs['result']['problems']:
            if ('rating' in prb) and (prb['rating'] >= minr) and (prb['rating'] <= maxr):
                ps.append(('https://codeforces.com/problemset/problem/' + str(prb['contestId']) + '/' + str(prb['index']), prb['rating']))

        for i in range(cnt):
            a = random.randint(0, len(ps))
            if mod == '-s':
                pss.append((ps[a][0], ps[a][1]))
            else:
                s += f'{ps[a][0]} = {str(ps[a][1])}\n'
            ps.pop(a)

        if mod == '-s':
            pss.sort(reverse = False, key = cmp)
            for i in range(len(pss)):
                s += f'{pss[i][0]} = {str(pss[i][1])}\n'

        await ctx.send(s)


def cmp(obj): #comporator for problems sorting
    return obj[1]


def setup(bot):
    bot.add_cog(codeforces(bot))
