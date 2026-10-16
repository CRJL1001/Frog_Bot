import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

#data handler----------------------------

from database import (
    add_ingredient,
    add_menu,
    add_recipie,
    remove_recipie,
    add_ingredient_to_recipie,
    add_recipie_to_menu,
    get_ingredients,
    get_menus,
    get_recipies,
    init_database,
    get_recipie,
    debug_tables,
    get_menu,
    get_menu_ingredients, remove_ingredient,
    remove_ingredient_from_recipie,
    remove_recipie_from_menu
)

class Menu(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot=bot


    #---------------------ingrédients

    @app_commands.command(name="ajouter_ingredient", description="Ajouter un ingrédient dans la cuisine")
    @app_commands.describe(
        nom="Nom de l'ingrédient, xx, xx, xx"
    )
    async def ajouter_ingredient(self, interaction: discord.Interaction, nom: str):
        ingredients = [name.strip() for name in nom.split(",")]

        if any(not name for name in ingredients):
            await interaction.response.send_message(" Chaque ingrédient doit avoir un nom", ephemeral=True)
            return

        added = []

        for name in ingredients:
            try:
                await add_ingredient(name)
                added.append(name)
            except Exception as error:
                print(f"Erreur lors de l'ajout de l'ingrédient : {error!r}")

        embed = discord.Embed(title="Ingrédients ajoutés dans la cuisine", color=discord.Color.yellow())
        for i in added:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="supprimer_ingredient", description="Supprimer un ingrédient de la cuisine")
    @app_commands.describe(
        nom="Nom de l'ingrédient, xx, xx"
    )
    async def supprimer_ingredient(self, interaction: discord.Interaction, nom: str):
        ingredients = [name.strip() for name in nom.split(",")]

        if any(not name for name in ingredients):
            await interaction.response.send_message(" Chaque ingrédient doit avoir un nom", ephemeral=True)
            return

        deleted = []

        for name in ingredients:
            try:
                await remove_ingredient(name)
                deleted.append(name)
            except Exception as error:
                print(f"Erreur lors de la suppression de l'ingrédient : {error!r}")

        embed = discord.Embed(title="Ingrédients supprimés de la cuisine", color=discord.Color.yellow())
        for i in deleted:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )
        await interaction.response.send_message(embed=embed)

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
        nom="Noms des recettes séparés par des virgules"
    )
    async def ajouter_recette(self, interaction: discord.Interaction, nom: str):
        recettes = [name.strip() for name in nom.split(",")]

        if any(not name for name in recettes):
            await interaction.response.send_message("Chaque recette doit avoir un nom", ephemeral=True)
            return

        added = []

        for name in recettes:
            try:
                await add_recipie(name)
                added.append(name)
            except Exception as error:
                print(f"Erreur lors de l'ajout de la recette : {error!r}")

        embed = discord.Embed(title="Recettes ajoutées dans la cuisine", color=discord.Color.yellow())
        for i in added:
            embed.add_field(
                name=f"{i}",
                value="",
                inline=True
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="supprimer_recette", description="Supprimer une recette de la cuisine")
    @app_commands.describe(
        nom="Noms des recettes séparés par des virgules"
    )
    async def supprimer_recette(self, interaction: discord.Interaction, nom: str):
        recettes = [name.strip() for name in nom.split(",")]

        if any(not name for name in recettes):
            await interaction.response.send_message("Chaque recette doit avoir un nom", ephemeral=True)
            return

        deleted = []

        for name in recettes:
            try:
                await remove_recipie(name)
                deleted.append(name)
            except Exception as error:
                print(f"Erreur lors de la suppression de la recette : {error!r}")

        embed = discord.Embed(title="Recettes supprimées de la cuisine", color=discord.Color.yellow())
        for i in deleted:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )
        await interaction.response.send_message(embed=embed)

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
    async def ajouter_ingredient_recette(self, interaction: discord.Interaction, nom_recette: str, nom_ingredient: str, count: str):
        ingredients = [ing.strip() for ing in nom_ingredient.split(",")]
        counts = [ co.strip() for co in count.split(",")]

        if any(not name for name in ingredients):
            await interaction.response.send_message("Chaque ingrédients doit avoir un nom", ephemeral=True)
            return
        elif any(not quant for quant in counts):
            await interaction.response.send_message("Chaque ingrédients doit avoir une quantitée", ephemeral=True)
            return

        size = len(ingredients)
        if size != len(counts):
            await interaction.response.send_message("il doit y avoir une qauntité pour chaque ingrédients", ephemeral=True)

        added = []

        for i in range(size):
            try:
                await add_ingredient_to_recipie(int(counts[i]), ingredients[i], nom_recette)
                added.append(f"{counts[i]} - {ingredients[i]}")
            except Exception as error:
                print(f"erreur lors de l'ajout de {ingredients[i]} : {error!r}")

        embed = discord.Embed(title=f"Ingrédients ajoutés à la recette {nom_recette} ", color=discord.Color.yellow())
        for i in added:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="supprimer_ingredient_recette", description="supprimer un ingrédient d'une recette")
    @app_commands.describe(
        nom_recette="Nom de la recette",
        nom_ingredient="Nom de l'ingrédient",
    )
    async def supprimer_ingredient_recette(self, interaction: discord.Interaction, nom_recette: str,
                                         nom_ingredient: str):
        ingredients = [ing.strip() for ing in nom_ingredient.split(",")]

        if any(not name for name in ingredients):
            await interaction.response.send_message("Chaque ingrédients doit avoir un nom", ephemeral=True)
            return

        removed = []

        for ing in ingredients:
            try:
                await remove_ingredient_from_recipie(ing, nom_recette)
                removed.append(ing)
            except Exception as error:
                print(f"ingrédient {ing} non supprimé : {error!r}")

        embed = discord.Embed(title=f"Ingrédients supprimé de la recette {nom_recette} ",
                              color=discord.Color.red())
        for i in removed:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )

        await interaction.response.send_message(embed=embed)



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
        nom_recette="Noms des recettes séparés par des virgules",
        menu="Id du menu",
        count="Quantités séparées par des virgules, dans le même ordre que les recettes"
    )
    async def ajouter_recette_menu(self, interaction: discord.Interaction, nom_recette: str, menu: int, count: str):
        recettes = [name.strip() for name in nom_recette.split(",")]
        counts = [quant.strip() for quant in count.split(",")]

        if any(not name for name in recettes):
            await interaction.response.send_message("Chaque recette doit avoir un nom", ephemeral=True)
            return
        if any(not quant for quant in counts):
            await interaction.response.send_message("Chaque recette doit avoir une quantité", ephemeral=True)
            return
        if len(recettes) != len(counts):
            await interaction.response.send_message("Il doit y avoir une quantité pour chaque recette", ephemeral=True)
            return

        try:
            counts = [int(quant) for quant in counts]
        except ValueError:
            await interaction.response.send_message(
                "Chaque quantité doit être un nombre entier",
                ephemeral=True
            )
            return

        added = []

        for recette, quant in zip(recettes, counts):
            try:
                await add_recipie_to_menu(quant, menu, recette)
                added.append(f"{quant} - {recette}")
            except Exception as error:
                print(f"Impossible d'ajouter la recette {recette} dans le menu #{menu} : {error!r}")

        embed = discord.Embed(title=f"Recettes ajoutées au menu #{menu}", color=discord.Color.yellow())
        for i in added:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="supprimer_recette_menu", description="Supprimer des recettes d'un menu")
    @app_commands.describe(
        nom_recette="Noms des recettes séparés par des virgules",
        menu="Id du menu",
    )
    async def supprimer_recette_menu(self, interaction: discord.Interaction, nom_recette: str, menu: int):
        recettes = [rec.strip() for rec in nom_recette.split(",")]

        if any(not name for name in recettes):
            await interaction.response.send_message("Chaque recette doit avoir un nom", ephemeral=True)
            return

        removed = []

        for rec in recettes:
            try:
                await remove_recipie_from_menu(rec, menu)
                removed.append(rec)
            except Exception as error:
                print(f"Recette {rec} non supprimée : {error!r}")

        embed = discord.Embed(title=f"Recettes supprimées du menu #{menu}",
                              color=discord.Color.red())
        for i in removed:
            embed.add_field(
                name=i,
                value="",
                inline=True
            )

        await interaction.response.send_message(embed=embed)

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

    @app_commands.command(name="afficher_ingredients_menu", description="Affiche un menu avec ses ingrédients")
    @app_commands.describe(
        id="Id du menu"
    )
    async def afficher_ingredients_menu(self, interaction: discord.Interaction, id: int):
        try:
            menu = await get_menu_ingredients(id)
            if not menu:
                await interaction.response.send_message(
                    "Impossible d'afficher le menu",
                    ephemeral=True
                )
                return

            embed = discord.Embed(title=f"Ingrédient du menu #{id} du {menu[0]['date_'].strftime('%d/%m/%Y')}", color=discord.Color.purple())
            for i in menu:
                embed.add_field(
                    name=f"{i['name']}",
                    value=f"{i['total']}",
                    inline=True
                )
            embed.add_field(
                name="Ne pas Oublier !",
                value="Eau, sopalin, dessert, gouter, etc !",
                inline=False
            )
            embed.add_field(
                name="Lien vers le drive",
                value="https://www.leclercdrive.fr/",
                inline=False
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
