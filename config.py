from dotenv import load_dotenv
import os

COMMAND_PREFIX="!"
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID"))
CREATE_CHANNEL_ID = int(os.getenv("CREATE_CHANNEL_ID"))
DAYS=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
DATA_FILE= "reminders.json"