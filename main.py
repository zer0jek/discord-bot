import discord
from discord.ext import commands
import os

# Pobranie tokena z zmiennej środowiskowej
TOKEN = os.getenv('MTQxODY5MTc4NDU2MDc0MjYxMQ.Gkrtnf.V1DJEfduKU9-MGYQ4AedgnCpprD58EaHn50Gpw')  # Ustaw DISCORD_TOKEN w hostingu

# Prefix dla komend bota
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Event uruchamiany po włączeniu bota
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

# Prosta komenda !ping
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')

# Komenda !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f'Cześć {ctx.author.mention}! 👋')

# Uruchomienie bota
bot.run(TOKEN)
