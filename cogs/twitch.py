import discord
from discord.ext import commands, tasks
import aiohttp

from config import TWITCH_ID, TWITCH_SECRET, TWITCH_CHANNEL

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_en_cours = set()
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
        params = "&".join(f"user_login={1}" for login in logins)
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
        rows = await self.get_streams()
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

    @commands.command(name="addstream")
    @commands.has_permissions(manage_guild=True)
    async def add_stream(self, ctx, login: str):
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
            await ctx.send(f"Le streamer **{login}** n'existe pas sur Twitch.")
            return

        await self.add_streamer(login)
        await ctx.send(f"**{login}** ajouté(e).")

    @commands.command(name="removestream")
    @commands.has_permissions(manage_guild=True)
    async def remove_stream(self, ctx, login: str):
        """Retire un streamer"""
        if await self.remove_streamer(login.lower().strip()):
            await ctx.send(f"**{login}** retiré(e)")
        else:
            await ctx.send(f"**{login}** n'est pas suivi(e)")

    @commands.command(name="liststreams")
    async def list_streams(self,ctx):
        """Liste les streamers surveillés"""
        rows = await self.get_streamers()
        if not rows:
            await ctx.send("Aucun streamers trouvés")
            return
        liste = '\n'.join(
            f"-[{r["twitch_login"]}](https://twitch.tv/{r["twitch_login"]})"
            for r in rows
        )
        await ctx.send(f"**Streamers surveillés :**\n{liste}")

async def setup(bot):
    await bot.add_cog(Twitch(bot))





