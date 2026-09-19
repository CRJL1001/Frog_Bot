import discord
from discord.ext import commands, tasks
from discord import app_commands
import json 
import os
from datetime import datetime, timedelta 
from dotenv import load_dotenv

#environment variable
COMMAND_PREFIX="!"
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
REMINDER_CHANNEL_ID = os.getenv("REMINDER_CHANNEL_ID")
CREATE_CHANNEL_ID = os.getenv("CREATE_CHANNEL_ID")

#bot initialisation
DATA_FILE= "reminders.json"

intents = discord.Intents.default()
bot = commands.bot(command_prefix=COMMAND_PREFIX, intents=intents)

#data handler

def load_reminders(): #load data from json file
    if os.path.exists(DATA_FILE): #data file existance verification
        with open(DATA_FILE, "r", encoding="utf-8") as f: #opening file on read only mode
            return json.load(f) #load data
    return [] #return data

def save_reminders(reminders): #save data in json file
    with open(DATA_FILE, "w", encoding="utf-8") as f: #open data file on write mode
        json.dump(reminders, f, ensure_ascii=False, indent=2) #write into data file 

#call verification

@tasks.loop(seconds=30) #repeating every 30 seconds
async def check_reminders(): #async methode
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
async 





