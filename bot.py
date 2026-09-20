import discord
from discord.ext import commands




#bot initialisation-------------------

from config import GUILD_ID, COMMAND_PREFIX, TOKEN


intents = discord.Intents.default()

class FrogBot(commands.Bot): #class of the bot
    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)

        for extension in ("cogs.utils", "cogs.tasks"):
            await self.load_extension(extension)

        self.tree.copy_global_to(guild=guild)

        # 🔎 DEBUG : combien de commandes sont enregistrées localement ?
        print(f"Commandes globales : {[c.name for c in self.tree.get_commands()]}")
        print(f"Commandes guild : {[c.name for c in self.tree.get_commands(guild=guild)]}")

        commands_list = await self.tree.sync(guild=guild)
        print(f"Commandes synchronisées ({len(commands_list)}) :")
        for command in commands_list:
            print(f"    - {command.name}")


bot = FrogBot( #creating instance of the bot
    command_prefix=COMMAND_PREFIX,
    intents=intents
)

@bot.event
async def on_ready():# async methode -> connecting bot
    print(f"Connecté en tant que {bot.user}") #connected logs


bot.run(TOKEN) #running the bot 





