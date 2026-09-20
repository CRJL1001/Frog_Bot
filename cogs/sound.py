import random
import asyncio
import discord
from discord.ext import commands

from config import SOUNDS, GUILD_ID, SOUND_CHANNEL_ID, VOCAL_SOUND_DELAY_INTERVAL

class Sounds(commands.Cog):
    def __init__(self, bot: commands.Bot ):
        self.bot = bot

    async def jouer_son(self):
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("Serveur introuvable")
            return

        channel = guild.get_channel(SOUND_CHANNEL_ID)
        if not channel:
            print("salon vocal introuvable")
            return

        if not channel.members:
            print("Personne dans le vocal")
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)
        if not voice_client or not voice_client.is_connected():
            voice_client = await channel.connect()

        await asyncio.sleep(0.2)

        son = random.choice(SOUNDS)
        source = discord.FFmpegPCMAudio(son)
        voice_client.play(source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.boucle_aleatoire())

    async def boucle_aleatoire(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            delai = random.randint(VOCAL_SOUND_DELAY_INTERVAL[0], VOCAL_SOUND_DELAY_INTERVAL[1])
            print(f'prochain son dans {delai} secondes...')
            await asyncio.sleep(delai)
            try:
                await self.jouer_son()
            except Exception as e:
                print(f" Erreur : {e}")

async def setup(bot):
    await bot.add_cog(Sounds(bot))