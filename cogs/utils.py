import discord
from discord.ext import commands, tasks
from discord import app_commands

class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot    

    @app_commands.command(name="ping_tb", description="ping vers Toad Bot")
    async def ping_tb(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Pong", ephemeral=True)
        except discord.HTTPException as error:
            print(f"Erreur serveur: {error}")


async def setup(bot:commands.Bot):
    print("setup utils appelé")
    await bot.add_cog(Utils(bot))