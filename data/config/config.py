import time
from json import load

with open("data/config/SECRET.json", "r") as f:
    secrets = load(f)

# Podstawowe parametry bota
TOKEN = secrets["DISCORD_TOKEN"]
commands_prefix = "!"
version = "1.0.3"
boot_date = time.strftime("%H:%M %d.%m.%Y UTC")
__cogs__ = [
    "data.modules.cogs.Administration",
    "data.modules.cogs.Utilities"
    ]
