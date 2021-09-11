#5a0a bot - Music cog
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests
import asyncio
import os

PATH = os.path.dirname(__file__) + '/data'
YDL_OPTIONS = {'format': 'bestaudio', 'playlistend': 50}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Player:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.message.channel

        self.next = asyncio.Event()

        self.playing = False
        self.info_msg = None
        self.looping = 0
        self.queue_pos = 0
        self.queue = []

    async def play_music(self):
        await self.bot.wait_until_ready()

        while len(self.queue) > 0:
            self.next.clear()
            self.playing = True

            if self.looping == 0 and self.queue_pos == len(self.queue):
                self.queue_pos = 0
                self.playing = False
                return
            elif self.looping == 1:
                self.queue_pos %= len(self.queue)

            song = self.queue[self.queue_pos]
            self.guild.voice_client.play(discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS), after=lambda e: self.bot.loop.call_soon_threadsafe(self.next.set))

            embed = discord.Embed(title=song['title'], url=song['url'], description='is now beeing played by ' + f"[{song['requester'].mention}]")
            self.info_msg = await self.channel.send(embed=embed)

            await self.next.wait()

            if self.looping != 2:
                self.queue_pos += 1

            await self.info_msg.delete()




class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.players = {}

    def get_player(self, ctx):
        if ctx.guild.id not in self.players:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        
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

    def generate_queue(self, page, queue, queue_pos):
        post = '```ml\n'
        for i in range(page * 10, min(page * 11 + 10, len(queue))):
            if i + 1 == queue_pos:
                post += '    ⬐ current track\n' + str(i + 1) + ') ' + queue[i]['title'] + '\n' + '    ⬑ current track\n'
            else:
                post += str(i + 1) + ') ' + queue[i]['title'] + '\n'

        if page * 11 + 10 >= len(queue):
            post += '\nThis is the end of queue!\n'
        else:
            post += f'\nThere {len(queue) - (page * 11 + 10)} songs left.'

        post += '```'
        return post


    async def destruct(self, guild):
        try:
            del self.players[guild.id]
        except KeyError:
            pass

        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vc = member.guild.voice_client

        if vc is not None:
            if len(vc.channel.members) == 1:
                try:
                    await self.bot.wait_for('voice_state_update', timeout=300, check=lambda m, b, a: a.channel == vc.channel)
                except:
                    try:
                        player = self.players[member.guild.id]
                        embed = discord.Embed(title='I decided to leave to conserve my energy.', description='Since there was no one in the voice chat.')
                        await player.channel.send(embed=embed)
                        await self.destruct(member.guild)
                    except:
                        pass
            if member == self.bot.user:
                if (not after.deaf):
                    await member.edit(deafen=True)
                    try:
                        player = self.players[member.guild.id]
                        embed = discord.Embed(title='Please, do not undeafen me.', description='It is for your privacy confidence.')
                        await player.channel.send(embed=embed)
                    except:
                        pass

    @commands.command(name='play', aliases=['c'])
    async def connect_(self, ctx):
        channel = ctx.author.voice.channel

        vc = ctx.voice_client

        if vc is not None:
            await vc.move_to(channel)
        else:
            await channel.connect()

        embed = discord.Embed(title=f'Connected to {channel}')
        await ctx.send(embed=embed, delete_after=20)
        
    @commands.command(name='play', aliases=['p'])
    async def play_(self, ctx, *query):
        query = ' '.join(query)

        vc = ctx.voice_client

        if vc is None:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        if len(query) != 0:
            player.queue += self.get_song(ctx, query)

        if not player.playing:
            ctx.bot.loop.create_task(player.play_music())

    @commands.command(name='stop', aliases=['s'])
    async def stop_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            await self.destruct(ctx.guild)

    @commands.command(name='next', aliases=['n', 'skip'])
    async def next_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            vc.stop()
            await ctx.invoke(self.play_)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            if not vc.is_paused():
                vc.pause()
                embed = discord.Embed(title='Player is paused.')
                await ctx.send(embed=embed)
            else:
                await ctx.invoke(self.resume_(ctx))

    @commands.command(name='resume')
    async def resume_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            if vc.is_paused():
                vc.resume()
                embed = discord.Embed(title='Resumed player.')
                await ctx.send(embed=embed)

    @commands.command(name='loop', aliases=['l'])
    async def loop_(self, ctx, mode):
        vc = ctx.voice_client

        if vc is not None:
            player = self.get_player(ctx)

            if mode.startswith('n'):
                player.looping = 0
                embed = discord.Embed(title='Loop is disabled')
                await ctx.send(embed=embed)

            if mode.startswith('q'):
                player.looping = 1
                embed = discord.Embed(title='Looping queue')
                await ctx.send(embed=embed)

            if mode.startswith('s'):
                player.looping = 2
                embed = discord.Embed(title='Looping song')
                await ctx.send(embed=embed)

    @commands.command(name='remove', aliases=['r'])
    async def remove_(self, ctx, *query):
        vc = ctx.voice_client

        if vc is not None:
            player = self.get_player(ctx)

            query = ''.join(query)
            if query.isnumeric() and int(query) <= len(player.queue):
                query = int(query)
                song = player.queue[query]
                del player.queue[query - 1]
                embed = discord.Embed(title=song.title, url=song.url, description='has been deleted from queue.')
                await ctx.send(embed=embed)
                if player.queue_pos == query - 1:
                    await ctx.invoke(self.next_)
            else:
                for i in range(len(player.queue)):
                    if query in player.queue[i]['title']:
                        song = player.queue[i]
                        del player.queue[i]
                        embed = discord.Embed(title=song.title, url=song.url, description='has been deleted from queue.')
                        await ctx.send(embed=embed)
                        if player.queue_pos == i:
                            await ctx.invoke(self.next_)
                        break

    @commands.command(name='jump', aliases=['j'])
    async def jump_(self, ctx, *query):
        vc = ctx.voice_client

        if vc is not None:
            player = self.get_player(ctx)

            query = ' '.join(query)
            if query.isnumeric() and int(query) <= len(player.queue):
                player.queue_pos = int(query) - 1
                await ctx.invoke(self.next_)
            else:
                for i in range(len(player.queue)):
                    if query in player.queue[i]['title']:
                        player.queue_pos = i
                        await ctx.invoke(self.next_)
                        break

    @commands.command(name='queue', aliases=['q'])
    async def queue_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            player = self.get_player(ctx)

            if len(player.queue) > 0:
                page = player.queue_pos // 11
                maxPage = len(player.queue) // 11 + 1
                
                msg = await ctx.send(self.generate_queue(page, player.queue, player.queue_pos))
                reactions = ['⏫', '🔼', '🔽', '⏬']
                for emoji in reactions:
                    await msg.add_reaction(emoji)

                flag = True

                while flag:
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=lambda reaction, user: str(reaction.emoji) in reactions and user.id != self.bot.user.id and msg == reaction.message)
                        if reaction.emoji == reactions[0]:
                            page = 0
                        elif reaction.emoji == reactions[1] and page != 0:
                            page -= 1
                        elif reaction.emoji == reactions[2] and page != maxPage - 1:
                            page += 1
                        elif reaction.emoji == reactions[3]:
                            page = maxPage - 1
                        await reaction.remove(user)
                        await msg.edit(content=self.generate_queue(page, player.queue, player.queue_pos))
                    except asyncio.TimeoutError:
                        flag = False

            else:
                await ctx.send('Queue is empty.')

    @commands.command(name='clear', aliases=['c'])
    async def clear_(self, ctx):
        vc = ctx.voice_client

        if vc is not None:
            player = self.get_player(ctx)

            if len(player.queue) != 0:
                player.queue.clear()
                player.queue_pos = 0
                vc.stop()
                player.playing = False
                embed = discord.Embed(title='Queue has been cleared.')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Queue is empty.')
                await ctx.send(embed=embed)

   
    @commands.Cog.listener() #activates when this cog in ready state
    async def on_ready(self):
        print('Music cog is active.')

def setup(bot):
    bot.add_cog(Music(bot))
