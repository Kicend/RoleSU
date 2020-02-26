import json
import os

# Stałe dla RoleSU
SERVERS_PREFIXES_DIR = "data/settings/servers_prefixes"
SERVERS_SETTINGS_FILES = "data/settings/servers_settings"
DEFAULT_SERVER_PREFIX = "!"
DEFAULT_SERVER_CONFIG = {"role_announcement_channel": "Nie ustawione",
                         "role_confirm_channel": "Nie ustawione",
                         "role_management_channel": "Nie ustawione"}

cache = {"waiting_messages": {}, "server_parameters": {}, "servers_settings": {}}
guild_list = []

async def startup(bot):
    for guild in bot.guilds:
        guild_list.append(str(guild.id))
        try:
            with open(SERVERS_SETTINGS_FILES + "/{}.json".format(str(guild.id)), "r") as f:
                guild_settings = json.load(f)
                cache["servers_settings"][guild.id] = guild_settings
        except (FileNotFoundError, FileExistsError):
            with open(SERVERS_SETTINGS_FILES + "/{}.json".format(str(guild.id)), "a") as f:
                json.dump(DEFAULT_SERVER_CONFIG, f, indent=4)
    os.makedirs(SERVERS_PREFIXES_DIR, exist_ok=True)
    os.makedirs(SERVERS_SETTINGS_FILES, exist_ok=True)
    if not os.path.isfile(SERVERS_PREFIXES_DIR + "/prefixes.json"):
        with open(SERVERS_PREFIXES_DIR + "/prefixes.json", "a") as f:
            servers_prefixes = {}
            for guild in guild_list:
                servers_prefixes[guild] = DEFAULT_SERVER_PREFIX
            json.dump(servers_prefixes, f, indent=4)

class GuildParameters:
    def __init__(self, guild_id):
        self.id = guild_id
        self.settings_filename = SERVERS_SETTINGS_FILES + "/{}.json".format(self.id)
        self.prefixes_filename = SERVERS_PREFIXES_DIR + "/prefixes.json"

    async def get_prefix(self):
        with open(self.prefixes_filename, "r") as f:
            prefixes = json.load(f)
            server_prefix = prefixes[str(self.id)]

        return server_prefix

    async def change_prefix(self, ctx, prefix: str):
        if os.path.isfile(self.prefixes_filename):
            with open(self.prefixes_filename, "r") as f:
                prefixes = json.load(f)
            with open(self.prefixes_filename, "w") as f:
                prefixes[str(self.id)] = prefix
                json.dump(prefixes, f, indent=4)
        else:
            with open(self.prefixes_filename, "a") as f:
                prefixes = {str(ctx.guild.id): prefix}
                json.dump(prefixes, f, indent=4)
        await ctx.send("Prefix został pomyślnie zmieniony na '{}'".format(prefix))
