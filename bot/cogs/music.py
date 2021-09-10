#5a0a bot - Music cog
import re
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests
import asyncio
import json
import os
import sqlite3

PATH = os.path.dirname(__file__) + '/data'
YDL_OPTIONS = {'format': 'bestaudio', 'playlistend': 50}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Player:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.message.channel

        self.info_msg = None
        self.looping = 0
        self.playing = False
        self.queue_pos = 0
        self.queue = []

    async def play_music(self):
        if len(self.queue) != 0:
            self.playing = True

            if self.looping == 0 and self.queue_pos == len(self.queue):
                self.queue_pos = 0
                self.playing = False
                embed = discord.Embed(title='End of queue.')
                self.info_msg = await self.channel.send(embed=embed)
                return
            elif self.looping == 1:
                self.queue_pos = (self.queue_pos + 1) % len(self.queue)

            song = self.queue[self.queue_pos]
            self.guild.voice_client.play(discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS), after=lambda e: self.play_music())

            await self.info_msg.delete()
            embed = discord.Embed(title=song['title'], url=song['url'], description='is now beeing played by' + song['requester'])
            self.info_msg = await self.channel.send(embed=embed)



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.players = []

    def get_player(self, ctx):
        if ctx.guild.id not in self.players:
            self.players[ctx.guild.id] = Player(ctx)
        
        return self.players[ctx.guild.id]

    def get_song(self, ctx, query):
        response = []
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                requests.get(query)
            except:
                info = ydl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
                response.append({'title': info['title'], 'url': info['formats'][0]['url'], 'requester': ctx.author})
            else:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    for i, entry in enumerate(info['entries']):
                        if i == 50:
                            break
                        response.append({'title': entry['title'], 'url': entry['formats'][0]['url'], 'requester': ctx.author})
                else:
                    response.append({'title': info['title'], 'url': info['formats'][0]['url'], 'requester': ctx.author})
            
            return response

    @commands.command()
    async def connect_(self, ctx):
        channel = ctx.author.voice.channel

        vc = ctx.voice_client

        if vc is not None:
            if vc.channel.id == channel.id:
                return
            elif vc.channel.id != channel.id:
                await vc.move_to(channel)
        else:
            await channel.connect() 

        embed = discord.Embed(title=f'Connected to {channel}')
        await ctx.send(embed=embed, delete_after=20)
        
    @commands.command()
    async def play_(self, ctx, *query):
        query = ' '.join(query)

        vc = ctx.voice_client

        if vc is None:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        if len(query) != 0:
            player.queue += self.get_song(ctx, query)

        player.play_music()
   
    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print('Music cog is active.')

def setup(bot):
    bot.add_cog(Music(bot))
