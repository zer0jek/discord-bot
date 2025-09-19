import discord
from discord.ext import commands
import pytesseract
from PIL import Image
import re
import os

TOKEN = "MTQxODY5MTc4NDU2MDc0MjYxMQ.Gkrtnf.V1DJEfduKU9-MGYQ4AedgnCpprD58EaHn50Gpw"  # <-- tutaj wklej token bota
CHANNEL_ID = 1418694785111429200  # <-- ID kanału do screenów

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Role po ID (podmień na swoje role z Discorda)
ROLE_THRESHOLDS = [
    (1000, 1418695474940219492),  # np. 2000+ pkt -> rola Legend
    (500, 1418695450709594382),  # np. 1000+ pkt -> rola Pro Player
    (100,  1418695425401294909),  # np. 500+ pkt -> rola Warrior
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

        # Szukamy liczb przy trybach gry
        clears_normal = clears_hard = clears_hell = clears_abyss = 0

        for line in text.splitlines():
            if "Normal" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    clears_normal = int(numbers[-1])
            elif "Hard" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    clears_hard = int(numbers[-1])
            elif "Hell" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    clears_hell = int(numbers[-1])
            elif "Abyss" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    clears_abyss = int(numbers[-1])

        # Liczymy punkty
        total_points = (
            clears_normal * 1 +
            clears_hard * 2 +
            clears_hell * 3 +
            clears_abyss * 4
        )

        # wybierz najwyższą rolę
        role_to_give = None
        for threshold, role_id in ROLE_THRESHOLDS:
            if total_points >= threshold:
                role_to_give = message.guild.get_role(role_id)
                break

        # usuń stare role z listy
        roles_to_remove = [message.guild.get_role(rid) for _, rid in ROLE_THRESHOLDS]
        roles_to_remove = [r for r in roles_to_remove if r in message.author.roles]
        if roles_to_remove:
            await message.author.remove_roles(*roles_to_remove)

        # nadaj nową rolę
        if role_to_give:
            await message.author.add_roles(role_to_give)
            try:
                await message.author.send(
                    f"🎉 Wykryłem u Ciebie {total_points} punktów "
                    f"(Normal={clears_normal}, Hard={clears_hard}, Hell={clears_hell}, Abyss={clears_abyss}).\n"
                    f"Otrzymałeś rolę **{role_to_give.name}** na serwerze {message.guild.name}!"
                )
            except:
                await message.channel.send(f"{message.author.mention}, nie mogłem wysłać Ci prywatnej wiadomości.")
        else:
            await message.channel.send(
                f"{message.author.mention}, masz {total_points} punktów – brak rangi."
            )

        # usuń wiadomość ze screenem
        await message.delete()
