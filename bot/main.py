import os
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
TOKEN = os.getenv('NzIyMjE0MTA3MjM5MDIyNjcy.Xuf0TQ.UrSOyJIIbqDzpObzVDkuDQaYDHk')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

if __name__ == "__main__":
    bot.run(TOKEN)
