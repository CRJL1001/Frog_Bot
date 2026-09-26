import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp

from database import(
    add_streamer,
    remove_streamer,
    get_streamers,
)

from config import TWITCH_ID, TWITCH_SECRET, TWITCH_CHANNEL

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lives_en_cours = set()
        self.twitch_token = None
        self.check_streams.start()

    def cog_unload(self):
        self.check_streams.cancel()

    #TWITCH API

    async def get_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": TWITCH_ID,
                    "client_secret": TWITCH_SECRET,
                    "grant_type": "client_credentials",
                },
            ) as resp:
                data = await resp.json()
                self.twitch_token = data["access_token"]

    async def get_streams(self, logins):
        headers = {
            "Client-ID": TWITCH_ID,
            "Authorization": f"Bearer {self.twitch_token}",
        }
        params = "&".join(f"user_login={login}" for login in logins)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.twitch.tv/helix/streams?{params}",
                headers=headers,
            ) as resp:
                if resp.status == 401:
                    await self.get_token()
                    return None
                data = await resp.json()
                return {s["user_login"]: s for s in data["data"]}

    #boucle de verif

    @tasks.loop(minutes=1)
    async def check_streams(self):
        rows = await get_streamers()
        if not rows:
            return
        if not self.twitch_token:
            await self.get_token()

        logins = [row["twitch_login"] for row in rows]
        streams = await self.get_streams(logins)
        if streams is None:
            return

        canal = self.bot.get_channel(TWITCH_CHANNEL)
        if not canal:
            return

        for row in rows:
            login = row["twitch_login"]

            if login in streams:
                if login not in self.lives_en_cours:
                    self.lives_en_cours.add(login)
                    stream = streams[login]
                    embed = discord.Embed(
                        title=stream["title"],
                        url=f"https://twitch.tv/{login}",
                        description=f"**{stream['user_name']}** est en live !",
                        color=0x9146FF,
                    )
                    embed.add_field(name="Jeu", value=stream["game_name"] or "Inconnu")
                    embed.set_thumbnail(
                        url=stream['thumbnail_url'].format(width=320, height=180)
                    )
                    await canal.send(embed=embed)
            else:
                self.lives_en_cours.discard(login)

    @check_streams.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    #Commandes discord

    @app_commands.command(name="addstream")
    @app_commands.default_permissions(manage_guild=True)
    async def add_stream(self, interaction: discord.Interaction, login: str):
        """Ajoute un streamer"""
        login = login.lower().strip()

        if not self.twitch_token:
            await self.get_token()
        headers = {
            "Client-ID": TWITCH_ID,
            "Authorization": f"Bearer {self.twitch_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.twitch.tv/helix/users?login={login}",
                headers=headers,
            ) as resp:
                data = await resp.json()

        if not data.get("data"):
            await interaction.response.send_message(f"le streamer {login} n'existe pas", ephemeral=True) #discord error message
            return

        await add_streamer(login)
        await interaction.response.send_message(f"{login} ajouté", ephemeral=True) #discord error message

    @app_commands.command(name="removestream")
    @app_commands.default_permissions(manage_guild=True)
    async def remove_stream(self, interaction: discord.Interaction, login: str):
        """Retire un streamer"""
        if await remove_streamer(login.lower().strip()):
            await interaction.response.send_message(f"streamer **{login}** retiré !", ephemeral=True) #discord error message
        else:
            await interaction.response.send_message(f"streamer {login} non suivi !", ephemeral=True) #discord error message

    @app_commands.command(name="liststreams")
    async def list_streams(self, interaction: discord.Interaction):
        """Liste les streamers surveillés"""
        rows = await get_streamers()
        if not rows:
            await interaction.response.send_message("Aucun streamers trouvés", ephemeral=True) #discord error message
            return
        liste = "\n".join(
            f"- [{r['twitch_login']}](https://twitch.tv/{r['twitch_login']})"
            for r in rows
        )
        await interaction.response.send_message(f"**Streamers surveillés :**\n{liste}", ephemeral=True) #discord error

async def setup(bot):
    await bot.add_cog(Twitch(bot))





