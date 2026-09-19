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
GUILD_ID = os.getenv("GUILD_ID")
REMINDER_CHANNEL_ID = os.getenv("REMINDER_CHANNEL_ID")
CREATE_CHANNEL_ID = os.getenv("CREATE_CHANNEL_ID")

#bot initialisation-------------------
DATA_FILE= "reminders.json"

intents = discord.Intents.default()
bot = commands.bot(command_prefix=COMMAND_PREFIX, intents=intents)

#data handler----------------------------

def load_reminders(): #load data from json file
    if os.path.exists(DATA_FILE): #data file existance verification
        with open(DATA_FILE, "r", encoding="utf-8") as f: #opening file on read only mode
            return json.load(f) #load data
    return [] #return data

def save_reminders(reminders): #save data in json file
    with open(DATA_FILE, "w", encoding="utf-8") as f: #open data file on write mode
        json.dump(reminders, f, ensure_ascii=False, indent=2) #write into data file 

#call verification-------------------------------

@tasks.loop(seconds=30) #repeating every 30 seconds
async def check_reminders(): #async methode -> verification of time to notify a task
    now = datetime.now() 
    channel = bot.get_channel(REMINDER_CHANNEL_ID) #notification doscord channel
    if channel is None: #if null return
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
            if r["assigned_to"]: #if assigned to somebody
                embed.add_field(name="Responsable", value=f"<@{r['assigned_to']}>") #add people field
            await channel.send(embed=embed) #sending message and awaiting for success response

    save_reminders(reminders) #saving json data

@bot.event

async def on_ready():# async methode -> connecting bot
    check_reminders.start() #start reminder_check methode
    await bot.tree.sync() #waiting for bot to start
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
    for i, j in enumerate(["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"])
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
        f"Rappel **{nom}** créé: tous les **{jour.name}** à **{heure}**" + (f"pour {responsable.mention}" if responsable else "")
    )

def compute_next_run(weekday, hour, minute): #return date of the next notification + 1 week
    now = datetime.now() 
    days_ahead = (weekday - now.weekday()) % 7 # day beetween now and next notify 
    target = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0) #creating target time 
    if target <= now : #if target is in the past add 1 week to reajust
        target += timedelta(weeks=1)
    return target









