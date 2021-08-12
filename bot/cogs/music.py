#5a0a bot - Music cog
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests
import asyncio
import json
import os

PATH = os.path.dirname(__file__) + '/data'
YDL_OPTIONS = {'format': 'bestaudio', 'playlistend': 50}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.is_looped = False
        self.is_playing = False
        self.queue_position = 0
        self.music_queue = []

        self.vc = None

    def add_music(self, query):
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                requests.get(query)
            except:
                info = ydl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
                self.music_queue.append({'title': info['title'], 'url': info['formats'][0]['url']})
            else:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        self.music_queue.append({'title': entry['title'], 'url': entry['formats'][0]['url']})
                else:
                    self.music_queue.append({'title': info['title'], 'url': info['formats'][0]['url']})

    def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            print(self.queue_position)

            if self.queue_position >= len(self.music_queue):
                if self.is_looped:
                    self.queue_position = 0
                else:
                    self.queue_position = 0
                    self.is_playing = False
                    return

            song = self.music_queue[self.queue_position]
            print(song['url'])
            self.queue_position += 1

            self.vc.play(discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS), after=lambda e: self.play_music())
            return song['title']
        else:
            self.is_playing = False
            return 'Queue is empty.'

    def generate_queue(self, page):
        post = '```ml\n'
        for i in range(page * 10, min(page * 11 + 10, len(self.music_queue))):
            if i + 1 == self.queue_position:
                post += '    ⬐ current track\n' + str(i + 1) + ') ' + self.music_queue[i]['title'] + '\n' + '    ⬑ current track\n'
            else:
                post += str(i + 1) + ') ' + self.music_queue[i]['title'] + '\n'

        if page * 11 + 10 >= len(self.music_queue):
            post += '\nThis is the end of queue!\n'
        else:
            post += f'\nThere {len(self.music_queue) - (page * 11 + 10)} songs left.'

        post += '```'
        return post


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.vc is None:
            return 

        if len(self.vc.channel.members) == 1:
            self.vc.stop()
            await self.vc.disconnect()
            self.vc = None
            self.is_playing = False
        
    @commands.command()
    async def connect(self, ctx):
        channel = ctx.author.voice.channel

        if self.vc != None:
            if self.vc.channel.id == channel.id:
                return
            else:
                await self.vc.move_to(channel)
        else:
            self.vc = await channel.connect()

        await ctx.send('Connected.')


    @commands.command()
    async def play(self, ctx, *args):
        query = ' '.join(args)
        if len(args) != 0:
            self.add_music(query)

        if self.vc == None:
            await ctx.invoke(self.connect)

        if not self.is_playing:
            await ctx.send(f'Now playing: **{self.play_music()}**')

    @commands.command()
    async def stop(self, ctx):
        if self.is_playing:
            self.vc.stop()
            await self.vc.disconnect()
            self.vc = None
            self.is_playing = False
            await ctx.send('Goodbye.')

    @commands.command()
    async def next(self, ctx):
        if self.is_playing:
            self.vc.stop()

        await ctx.invoke(self.play)

    @commands.command()
    async def queue(self, ctx):
        if len(self.music_queue) > 0:
            page = self.queue_position // 11
            maxPage = len(self.music_queue) // 11 + 1
               
            msg = await ctx.send(self.generate_queue(page))
            reactions = ['⏫', '🔼', '🔽', '⏬']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            flag = True

            while flag:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 60, check = lambda reaction, user: str(reaction.emoji) in reactions and user.id != self.bot.user.id and msg == reaction.message)
                    if reaction.emoji == reactions[0]:
                        page = 0
                    elif reaction.emoji == reactions[1] and page != 0:
                        page -= 1
                    elif reaction.emoji == reactions[2] and page != maxPage - 1:
                        page += 1
                    elif reaction.emoji == reactions[3]:
                        page = maxPage - 1
                    await reaction.remove(user)
                    print(page)
                    print(maxPage)
                    await msg.edit(content=self.generate_queue(page))
                except asyncio.TimeoutError:
                    flag = False

        else:
            await ctx.send('Queue is empty.')

    @commands.command()
    async def loop(self, ctx):
        self.is_looped = not self.is_looped
        if self.is_looped:
            await ctx.send('Now looping queue.')
        else:
            await ctx.send('Stoped looping queue.')

    @commands.command()
    async def remove(self, ctx, query):
        if query.isnumeric() and int(query) <= len(self.music_queue):
            del self.music_queue[int(query) - 1]
            await ctx.invoke(self.next)
        else:
            for i in range(len(self.music_queue)):
                if query in self.music_queue[i]['title']:
                    del self.music_queue[i]
                    await ctx.invoke(self.next)
                    break

    @commands.command()
    async def jump(self, ctx, query):
        if query.isnumeric() and int(query) <= len(self.music_queue):
            self.queue_position = int(query) - 1
            await ctx.invoke(self.next)
        else:
            for i in range(len(self.music_queue)):
                if query in self.music_queue[i]['title']:
                    self.queue_position = i
                    await ctx.invoke(self.next)
                    break

    @commands.command()
    async def clear(self, ctx):
        if len(self.music_queue) != 0:
            self.music_queue.clear()
            self.queue_position = 0
            self.vc.stop()
            await ctx.send('Queue has been cleared.')
        else:
            await ctx.send('Queue is empty.')

    @commands.command()
    async def queue_save(self, ctx, name = ''):
        with open(PATH + '/queues.json', 'r', encoding='utf-8') as file:
            queues = json.load(file)
        
        if name != '' and name not in queues:
            queues[name] = [song['title'] for song in self.music_queue]
            await ctx.send('Queue was saved.')
        else:
            await ctx.send('Failed to save queue.')
        
        with open(PATH + '/queues.json', 'w', encoding='utf-8') as file:
            json.dump(queues, file)  

    @commands.command()
    async def queue_load(self, ctx, name = ''):
        with open(PATH + '/queues.json', 'r', encoding='utf-8') as file:
            queues = json.load(file)
        
        if name != '' and name in queues:
            for song in queues[name]:
                self.add_music(song)
            await ctx.send('Queue has been loaded.')
        else:
            await ctx.send('Failed to load queue.')

    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print('Music cog is active.')

def setup(bot):
    bot.add_cog(Music(bot))
