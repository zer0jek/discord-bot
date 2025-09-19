import discord
from discord.ext import commands
import pytesseract
from PIL import Image
import re
import os

TOKEN = "TWOJ_TOKEN"  # <-- tutaj wklej token bota
CHANNEL_ID = 123456789012345678  # <-- ID kanału, na którym bot ma działać

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# progi clears -> role (od najwyższego do najniższego)
ROLE_THRESHOLDS = [
    (1000, "Legend"),
    (500, "Pro Player"),
    (100, "Warrior")
]

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    if message.attachments:
        attachment = message.attachments[0]
        filepath = f"./{attachment.filename}"
        await attachment.save(filepath)

        # OCR
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        os.remove(filepath)

        # znajdź clears
        clears = max([int(x) for x in re.findall(r"\d+", text)], default=0)

        # ustal rolę
        role_to_give = None
        for threshold, role in ROLE_THRESHOLDS:
            if clears >= threshold:
                role_to_give = discord.utils.get(message.guild.roles, name=role)
                break

        # usuń stare role z listy
        roles_to_remove = [discord.utils.get(message.guild.roles, name=r) for _, r in ROLE_THRESHOLDS]
        roles_to_remove = [r for r in roles_to_remove if r in message.author.roles]

        if roles_to_remove:
            await message.author.remove_roles(*roles_to_remove)

        # dodaj nową rolę
        if role_to_give:
            await message.author.add_roles(role_to_give)
            try:
                await message.author.send(
                    f"🎉 Wykryłem u Ciebie **{clears} clears**.\n"
                    f"Otrzymałeś nową rolę **{role_to_give.name}** na serwerze {message.guild.name}!"
                )
            except:
                await message.channel.send(f"{message.author.mention}, nie mogłem wysłać Ci prywatnej wiadomości.")
        else:
            await message.channel.send(f"{message.author.mention}, masz {clears} clears – brak rangi.")

        # usuń wiadomość ze screenem
        await message.delete()
