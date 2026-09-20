import random
import asyncio
import discord
from discord.ext import commands

from config import SOUNDS, GUILD_ID, SOUND_CHANNEL_ID, VOCAL_SOUND_DELAY_INTERVAL

class Sounds(commands.Cog):
    def __init__(self, bot: commands.Bot ):
        self.bot = bot
        self.sounds_enabled=True

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

    async def boucle_aleatoire(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            delai = random.randint(VOCAL_SOUND_DELAY_INTERVAL[0], VOCAL_SOUND_DELAY_INTERVAL[1])

            if not self.sounds_enabled:
                print("Sons désactivés")
                await asyncio.sleep(30)
                continue

            print(f'prochain son dans {delai} secondes...')
            await asyncio.sleep(delai)
            try:
                await self.jouer_son()
            except Exception as e:
                print(f" Erreur : {e}")
                await asyncio.sleep(20)

    @discord.app_commands.command(name="sounds", description="Activer ou Désactiver les sons aléatoires")
    @discord.app_commands.describe(etat="Choisis d'activer ou de désactiver les sons aléatoires")
    @discord.app_commands.choices(etat=[
        discord.app_commands.Choice(name="Activer", value="on"),
        discord.app_commands.Choice(name="Désactiver", value="off")
    ])
    async def sounds(self, interaction: discord.Interaction, etat: str):
        self.sounds_enabled = (etat == "on")

        if not self.sounds_enabled:
            guild = self.bot.get_guild(GUILD_ID)
            if guild:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)
                if voice_client and voice_client.is_connected():
                    voice_client.stop()
                    await voice_client.disconnected()

        emoji = "🎶" if self.sounds_enabled else "🔇"
        await interaction.response.send_message(f"{emoji} - Sons Vocaux Aléatoires {"activé" if self.sounds_enabled else "désactivé"}")



async def setup(bot):
    print("Setup sound appelé")
    cog=Sounds(bot)
    await bot.add_cog(cog)
    bot.loop.create_task(cog.boucle_aleatoire())