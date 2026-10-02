import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

#data handler----------------------------

from database import (
    add_ingredient,
    add_menu,
    add_recipie,
    add_ingredient_to_recipie,
    add_recipie_to_menu,
    get_ingredients,
    get_menus,
    get_recipies,
    init_database
)

class Menu(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot=bot


    @app_commands.command(name="ajouter_ingredient", description="Ajouter un ingrédient dans la cuisine")
    @app_commands.describe(
        nom="Nom de l'ingrédient"
    )
    async def ajouter_ingredient(self, interaction: discord.Interaction, nom: str):
        try:
            await add_ingredient(nom)
        except Exception as error:
            print(f"Erreur lors de l'ajout de l'ingrédient : {error!r}")
            await interaction.response.send_message(
                "Impossible d'ajouter l'ingrédient dans la cuisine ou déjà présent",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Ingrédient **{nom}** ajouté dans la cuisine !"
        )


    @app_commands.command(name="liste_ingredients", description="Lister les ingrédients de la cuisine")
    async def liste_ingredients(self, interaction: discord.Interaction):
        ingredients = await get_ingredients()
        if not ingredients:
            await interaction.response.send_message("Aucun ingrédient enregistrés", ephemeral=True)
            return
        embed = discord.Embed(title="Ingrédients de la cuisine", color=discord.Color.green())
        for i in ingredients:
            embed.add_field(
                name=f"#{i['id_ingredient']}",
                value=f"{i['name']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)



async def setup(bot: commands.Bot):
    print("setup menu appelé")
    await init_database()
    cog = Menu(bot)
    await bot.add_cog(cog)
