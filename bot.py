import discord
from discord.ext import commands, tasks
from discord import app_commands
import json 
import os
from datetime import datetime, timedelta 
from dotenv import load_dotenv

#environment variable-----------------------
COMMAND_PREFIX="!"
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID"))
CREATE_CHANNEL_ID = int(os.getenv("CREATE_CHANNEL_ID"))
DAYS=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

#bot initialisation-------------------
DATA_FILE= "/app/data/reminders.json"
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

intents = discord.Intents.default()

class FrogBot(commands.Bot): #class of the bot
    async def setup_hook(self): #hook to load commands in the bot
        guild = discord.Object(id=GUILD_ID) #serveur

        self.tree.copy_global_to(guild=guild) #params
        commands = await self.tree.sync(guild=guild) #synchro commands

        print("Commandes synchronisées :")
        for command in commands: #display commands hooked 
            print(f"    - {command.name}")


bot = FrogBot( #creating instance of the bot
    command_prefix=COMMAND_PREFIX,
    intents=intents
)


#data handler----------------------------

def load_reminders(): #load data from json file
    if os.path.exists(DATA_FILE): #data file existance verification
        with open(DATA_FILE, "r", encoding="utf-8") as f: #opening file on read only mode
            return json.load(f) #load data
    print("load_reminders OK")
    return [] #return data

def save_reminders(reminders): #save data in json file
    with open(DATA_FILE, "w", encoding="utf-8") as f: #open data file on write mode
        json.dump(reminders, f, ensure_ascii=False, indent=2) #write into data file 

#tasks verification-------------------------------

@tasks.loop(seconds=30) #repeating every 30 seconds
async def check_reminders(): #async methode -> verification of time to notify a task
    print(f"->Reminders for now notified at {str(datetime.now())}")
    now = datetime.now() 
    reminder_channel = bot.get_channel(REMINDER_CHANNEL_ID) #notification doscord channel
    if reminder_channel is None: #if null return
        return

    reminders = load_reminders() #methode to load data
    for r in reminders: #for every tasks
        target = datetime.strptime(r["next_run"], "%Y-%m-%d %H:%M") #date of the task to be notified = "next run" field in json object and then format 
        if now >= target: #if it's the time to notify
            embed = discord.Embed( #create a discord message
                title="Rappel de la tâche !", 
                description=f"**{r['name']}**\n{r['description'] or ''}", 
                color=discord.Color.orange()
            )
            if r.get("assigned_to"): #if assigned to somebody
                embed.add_field(name="Responsable", value=f"<@{r['assigned_to']}>") #add people field
            try:
                await reminder_channel.send(embed=embed) #sending message and awaiting for success response
            except discord.Forbidden:
                print(
                    f"Permissions insuffisantes dans le salon "
                    f"{reminder_channel} -> {reminder_channel.id}"
                )
                return
            except discord.HTTPException as error:
                print(f"Erreur discord lors de l'envoi : {error}")
                return 

            r["next_run"] = compute_next_run(
                r['weekday'],
                r["hour"],
                r['minute']
            ).strftime("%Y-%m-%d %H:%M")

    save_reminders(reminders) #saving json data

@check_reminders.before_loop #waiting before loop that the bot is ready
async def before_check_reminders():
    await bot.wait_until_ready()

@bot.event
async def on_ready():# async methode -> connecting bot
    if not check_reminders.is_running(): #run only if service is offline
        check_reminders.start()
    print(f"Connecté en tant que {bot.user}") #connected logs

#bot commands-----------------------------

@bot.tree.command(name="ajouter_rappel_hebdo", description="Ajouter un rappel hebdomadaire") #commands call definition
@app_commands.describe( #description of command on discord
    nom="Nom de la tâche (ex: Changer les draps)", #field and exemple
    jour="Jour de la semaine : [lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche]",
    heure="Heure au format -> HH:MM (ex: 20:30)",
    description="Description optionnelle",
    responsable="Mentionner la personne responsable (ex: @jean_23)"
)

@app_commands.choices(jour=[ #enumaration for day field
    app_commands.Choice(name=j, value=i) 
    for i, j in enumerate(DAYS)
])

async def ajouter_rappel(interaction: discord.Interaction, nom: str, jour: app_commands.Choice[int], heure: str, description: str = None, responsable: discord.Member = None): #async methode -> add reminder
    try:
        h, m = map(int, heure.split(":")) #split hour 13:34 -> h=13, m=34
        if not (0 <= h < 24 and 0 <= m < 60): # verification h beetween 0 and 23 & m beetween 0 and 59
            raise ValueError #error throw
    except ValueError: #error catch
        await interaction.response.send_message("Format d'heure invalide, Utilisez HH:MM (ex : 18:30)", ephemeral=True) #discord error message
        return

    reminders = load_reminders() #load reminders data
    new_id = max((r['id'] for r in reminders), default=0) + 1 #search max id in reminders id tab and add 1 to it
    reminders.append({ #adding to json
        "id": new_id,
        "name": nom,
        "description": description, 
        "assigned_to": responsable.id if responsable else None,
        "weekday": jour.value,
        "hour": h,
        "minute": m,
        "next_run": compute_next_run(jour.value, h, m).strftime("%Y-%m-%d %H:%M")
    })
    save_reminders(reminders) #saving to file

    await interaction.response.send_message( #confirmation discord message
        f"Rappel **{nom}** créé: tous les **{jour.name}** à **{heure}**" + (f" pour {responsable.mention}" if responsable else "")
    )

def compute_next_run(weekday, hour, minute): #return date of the next notification + 1 week
    now = datetime.now() 
    days_ahead = (weekday - now.weekday()) % 7 # day beetween now and next notify 
    target = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0) #creating target time 
    if target <= now : #if target is in the past add 1 week to reajust
        target += timedelta(weeks=1)
    return target

@bot.tree.command(name="liste_rappels", description="Voir les rappels") #command to see the list of reminders
async def liste_rappels(interaction: discord.Interaction): #async methode -> print list of reminders
    print("list index")
    reminders = load_reminders() #load data from file
    if not reminders: #if null
        await interaction.response.send_message("Aucun rappel enregistré.", ephemeral=True) #send discord message
        return
    embed = discord.Embed(title="Rappels de tâches", color=discord.Color.blue()) #discord base message
    for r in sorted(reminders, key=lambda x: x["next_run"]): #for all reminders
        who = f" - <@{r['assigned_to']}>" if r.get('assigned_to') else "" #assigned person field
        embed.add_field( #adding infos fields
            name=f"#{r['id']} - {r['name']}",
            value=f"{DAYS[r['weekday']]} à {r['hour']:02d}:{r['minute']:02d}{who}",
            inline=False
        )
    await interaction.response.send_message(embed=embed) #await for the message to be send in discord


@bot.tree.command(
    name="supprimer_rappel",
    description="Supprimer un rappel par son ID"
)
@app_commands.describe(id="ID du rappel à supprimer")
async def supprimer_rappel(
    interaction: discord.Interaction,
    id: int
):
    print(f"Suppression demandée : {id}")

    reminders = load_reminders()

    reminders_new = [
        r for r in reminders
        if int(r["id"]) != int(id)
    ]

    if len(reminders_new) == len(reminders):
        await interaction.response.send_message(
            f"Aucun rappel trouvé avec l'ID #{id}.",
            ephemeral=True
        )
        return

    save_reminders(reminders_new)
    print(f"Rappel #{id} supprimé")

    await interaction.response.send_message(
        f"Rappel #{id} supprimé."
    )

bot.run(TOKEN) #running the bot 





