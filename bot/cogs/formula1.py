#5a0a bot - F1 cog
from urllib import response
from discord.ext import commands
import json
import os
import requests
from datetime import datetime
from tabulate import tabulate

path = os.path.dirname(__file__) + '/data'

class f1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print('F1 cog is active.')

    @commands.command(aliases=['standings'])
    async def f1_standings(self, ctx):
        try:
            standingsLists = json.loads(requests.get('http://ergast.com/api/f1/current/driverStandings.json').text)['MRData']['StandingsTable']['StandingsLists'][0]
        except requests.exceptions.HTTPError:
            await ctx.send('Formula 1 Server Error.')
            return

        season = standingsLists['season']
        round = standingsLists['round']

        table = [['#', 'driver', 'points wins', 'constructor']]

        response = f'**FIA Formula 1 {season} World championship. Standings on round {round}.**\n```md\n'


        for entry in standingsLists['DriverStandings']:
            table.append([f"{entry['position']}", f"{entry['Driver']['givenName']} {entry['Driver']['familyName']}", f"[{entry['points']}]({entry['wins']})", f"<{entry['Constructors'][0]['name']}>"])

        response += tabulate(table, headers='firstrow') + '\n```'

        await ctx.send(response)
    
        try:
            standingsLists = json.loads(requests.get('http://ergast.com/api/f1/current/constructorStandings.json').text)['MRData']['StandingsTable']['StandingsLists'][0]
        except requests.exceptions.HTTPError:
            return

        table = [['#', 'constructor', 'points wins', 'country']]
        response = '```md\n'

        for entry in standingsLists['ConstructorStandings']:
            table.append([f"{entry['position']}", entry['Constructor']['name'], f"[{entry['points']}]({entry['wins']})", f"<{entry['Constructor']['nationality']}>"])
        
        response += tabulate(table, headers='firstrow') + '\n```'

        await ctx.send(response)

    @commands.command(aliases=['schedule'])
    async def f1_schedule(self, ctx):
        try:
            schedule = json.loads(requests.get(f'http://ergast.com/api/f1/current.json').text)['MRData']['RaceTable']['Races']
        except requests.exceptions.HTTPError:
            await ctx.send('Formula 1 Server Error.')
            return

        season = schedule[0]['season']
        table = [['round', 'name', 'date time', 'circuit']]

        response = f'**FIA Formula 1 World Championship. Season {season} schedule.**\n```md\n'

        currentDate = datetime.now()

        i = 0

        for race in schedule:
            if i == 10:
                break

            date = race['date']
            time = str((int(race['time'][:2]) + 3) % 24) + ':00:00MSK'

            raceDate = datetime.strptime(date, '%Y-%m-%d')

            if currentDate <= raceDate:
                table.append([f"{race['round']}", race['raceName'], f"[{date}]({time})", f"<{race['Circuit']['circuitName']}>"])
                i += 1

            if i == 1:
                table.append([''])

        response += tabulate(table, headers='firstrow') + '\n```'
        
        await ctx.send(response)

def setup(bot):
    bot.add_cog(f1(bot))
