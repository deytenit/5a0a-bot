#wndrx bot - F1 cog
import discord
from discord.ext import commands
import json
import os
import urllib
import random
from urllib.request import urlopen

path = os.path.dirname(__file__) + '/data'

class f1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print(f'F1 cog is active.')

    @commands.command()
    async def f1_drivers(self, ctx):
        try:
            drivers = json.loads(urlopen(f'http://ergast.com/api/f1/current/driverStandings.json').read())['StandingsTable']['StandingsLists'][0]
            season = drivers['season']
            round = drivers['round']
            standings = f'**FIA Formula 1 {season} championship. Standings on round {round}.**\n'
            standings += '```haskel\n' + '# | wins | driver | points | constructor\n' + '________________________________________\n'
            for pos in drivers['DriverStandings']:
                num = pos['position']
                tag = pos['Driver']['code']
                wins = pos['wins']
                points = pos['points']
                constructor = pos['Constructors'][0]['name']
                standings += f'{num} | {wins} | {tag} | {points} | {constructor}\n'
            
            standings += '________________________________________```'

            await ctx.send(standings)
        except urllib.error.HTTPError:
            await ctx.send('Server is down.')

def setup(bot):
    bot.add_cog(f1(bot))
