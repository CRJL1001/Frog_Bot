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
    init_database,
    get_recipie,
    debug_tables,
    get_menu
)

class Menu(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot=bot


    #---------------------ingrédients

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

    #--------------------recettes

    @app_commands.command(name="ajouter_recette", description="Ajouter une recette dans la cuisine")
    @app_commands.describe(
        nom="Nom de la recette"
    )
    async def ajouter_recette(self, interaction: discord.Interaction, nom: str):
        try:
            await add_recipie(nom)
        except Exception as error:
            print(f"Erreur lors de l'ajout de la recette : {error!r}")
            await interaction.response.send_message(
                "Impossible d'ajouter la recette dans la cuisine ou déjà présent",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Recette **{nom}** ajouté dans la cuisine !"
        )

    @app_commands.command(name="liste_recettes", description="Lister les recettes de la cuisine")
    async def liste_recettes(self, interaction: discord.Interaction):
        recettes = await get_recipies()
        if not recettes:
            await interaction.response.send_message("Aucune recette enregistrée", ephemeral=True)
            return
        embed = discord.Embed(title="Recettes de la cuisine", color=discord.Color.yellow())
        for i in recettes:
            embed.add_field(
                name=f"#{i['id_recipie']}",
                value=f"{i['name']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ajouter_ingredient_recette", description="Ajouter une quantité d'ingrédient dans une recette")
    @app_commands.describe(
        nom_recette="Nom de la recette",
        nom_ingredient="Nom de l'ingrédient",
        count="quantité de l'ingrédient dans la recette"
    )
    async def ajouter_ingredient_recette(self, interaction: discord.Interaction, nom_recette: str, nom_ingredient: str, count: int):
        try:
            await add_ingredient_to_recipie(count, nom_ingredient, nom_recette)
        except Exception as error:
            print(f"Impossible d'ajouter l'ingrédient {nom_ingredient} dans {nom_recette} : {error!r}")
            await interaction.response.send_message(
                "Impossible d'ajouter l'ingrédient dans la recette",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Ingrédient **{nom_ingredient}** ajouté dans la recette : **{nom_recette}** !"
        )



    @app_commands.command(name="afficher_recette", description="Affiche une recette avec ses ingrédients")
    @app_commands.describe(
        nom="Nom de la recette"
    )
    async def afficher_recette(self, interaction: discord.Interaction, nom: str):
        try:
            recette = await get_recipie(nom)
            if not recette:
                await interaction.response.send_message(
                    "Impossible d'afficher la recette",
                    ephemeral=True
                )
                return

            embed = discord.Embed(title=f"Recette {nom} :", color=discord.Color.pink())
            for i in recette:
                embed.add_field(
                    name=f"{i['name']}",
                    value=f"{i['count']}",
                    inline=True
                )
            await interaction.response.send_message(embed=embed)

        except Exception as error:
            print(f"Impossible d'afficher la recette {nom} : {error!r}")
            await interaction.response.send_message(
                "Impossible d'afficher la recette",
                ephemeral=True
            )




    #--------------------menus

    @app_commands.command(name="ajouter_menu", description="Ajouter un menu dans la cuisine")
    async def ajouter_menu(self, interaction: discord.Interaction):
        try:
            i = await add_menu()
        except Exception as error:
            print(f"Erreur lors de l'ajout du menu : {error!r}")
            await interaction.response.send_message(
                "Impossible d'ajouter le menu dans la cuisine",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Menu **{i}** ajouté dans la cuisine !"
        )

    @app_commands.command(name="liste_menu", description="Lister les menus de la cuisine")
    async def liste_menus(self, interaction: discord.Interaction):
        menus = await get_menus()
        if not menus:
            await interaction.response.send_message("Aucun menu enregistré", ephemeral=True)
            return
        embed = discord.Embed(title="Menu de la cuisine", color=discord.Color.blue())
        for i in menus:
            embed.add_field(
                name=f" menu n° #{i['id_menu']}",
                value=f" créer le {i['date_']}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ajouter_recette_menu", description="Ajouter une recette dans un menu")
    @app_commands.describe(
        nom_recette="Nom de la recette",
        menu="Id du menu",
        count="quantité de la recette dans le menu"
    )
    async def ajouter_recette_menu(self, interaction: discord.Interaction, nom_recette: str, menu: int, count: int):
        try:
            await add_recipie_to_menu(count, menu, nom_recette)
        except Exception as error:
            print(f"Impossible d'ajouter la recette {nom_recette} dans le menu #{menu} : {error!r}")
            await interaction.response.send_message(
                "Impossible d'ajouter la recette dans le menu",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Recette **{nom_recette}** ajouté dans le menu : **#{menu}** !"
        )



    @app_commands.command(name="afficher_menu", description="Affiche un menu avec ses recettes")
    @app_commands.describe(
        id="Id du menu"
    )
    async def afficher_menu(self, interaction: discord.Interaction, id: int):
        try:
            menu = await get_menu(id)
            if not menu:
                await interaction.response.send_message(
                    "Impossible d'afficher le menu",
                    ephemeral=True
                )
                return

            embed = discord.Embed(title=f"Menu #{id} du {menu[0]['date_'].strftime("%d/%m/%Y")}", color=discord.Color.red())
            for i in menu:
                embed.add_field(
                    name=f"{i['name']}",
                    value=f"{i['count']}",
                    inline=True
                )
            await interaction.response.send_message(embed=embed)

        except Exception as error:
            print(f"Impossible d'afficher le menu  #{id} : {error!r}")
            await interaction.response.send_message(
                "Impossible d'afficher le menu",
                ephemeral=True
            )






async def setup(bot: commands.Bot):
    print("setup menu appelé")
    await init_database()
    cog = Menu(bot)
    await bot.add_cog(cog)
