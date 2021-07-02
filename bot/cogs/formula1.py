#5a0a bot - F1 cog
from discord.ext import commands
import json
import os
import requests
from datetime import datetime

path = os.path.dirname(__file__) + '/data'

class f1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print('F1 cog is active.')

    @commands.command()
    async def f1_drivers(self, ctx):
        try:
            drivers = json.loads(requests.get('http://ergast.com/api/f1/current/driverStandings.json').text)
        except requests.exceptions.HTTPError:
            await ctx.send('Formula 1 Server Error.')
            return

        drivers = drivers['MRData']['StandingsTable']['StandingsLists'][0]

        season = drivers['season']
        round = drivers['round']

        ansDrivers = f'**FIA Formula 1 {season} championship. Standings on round {round}.**\n'

        ansDrivers += '```md\n' + '# | driver | points wins | constructor\n' + '=======================================\n'

        for pos in drivers['DriverStandings']:
            num = pos['position']
            tag = pos['Driver']['code']
            wins = pos['wins']
            points = pos['points']
            constructor = pos['Constructors'][0]['name']
            ansDrivers += f'{num}. | "{tag}" | [{points}]({wins}) | <{constructor}>\n'
        
        ansDrivers += '________________________________________```'

        await ctx.send(ansDrivers)

    @commands.command()
    async def f1_schedule(self, ctx):
        try:
            schedule = json.loads(requests.get(f'http://ergast.com/api/f1/current.json').text)
        except requests.exceptions.HTTPError:
            await ctx.send('Formula 1 Server Error.')
            return

        schedule = schedule['MRData']['RaceTable']['Races']
        season = schedule[0]['season']

        ansSchedule = f'**FIA Formula 1 {season} Schedule.**\n'
        ansSchedule += '```md\n' + 'round | name | date time | circuit\n' + '====================================\n'

        currentDate = datetime.now()

        flag = False

        i = 0

        for race in schedule:
            if i == 10:
                break

            round = race['round']
            name = race['raceName']
            date = race['date']
            time = race['time']
            circuit = race['Circuit']['circuitName']

            raceDate = datetime.strptime(date, '%Y-%m-%d')

            if flag:
                ansSchedule += f'{round}. | {name} | [{date}]({time}) | <{circuit}>\n'
                i += 1
            elif currentDate <= raceDate:
                flag = True
                ansSchedule += f'= {round}. | {name} | [{date}]({time}) | <{circuit}> <= Next Race\n' + '====================================\n'
            
        ansSchedule += '____________________________________```\n'
        
        await ctx.send(ansSchedule)

def setup(bot):
    bot.add_cog(f1(bot))
