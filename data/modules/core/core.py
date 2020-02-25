import json
import os

# Stałe dla RoleSU
SERVERS_PREFIXES_FILE = "data/settings/servers_prefixes/prefixes.json"
SERVERS_SETTINGS_FILES = "data/settings/servers_prefixes"
DEFAULT_SERVER_PREFIX = "!"

cache = {"waiting_messages": {}}
guild_list = []

async def startup(bot):
    for guild in bot.guilds:
        guild_list.append(str(guild.id))
    if not os.path.isfile(SERVERS_PREFIXES_FILE):
        with open(SERVERS_PREFIXES_FILE, "a") as f:
            servers_prefixes = {}
            for guild in guild_list:
                servers_prefixes[guild] = DEFAULT_SERVER_PREFIX
            json.dump(servers_prefixes, f, indent=4)

class GuildParameters:
    def __init__(self, guild_id):
        self.id = guild_id
        self.settings_filename = SERVERS_SETTINGS_FILES + "/{}.json".format(self.id)
        self.prefixes_filename = SERVERS_PREFIXES_FILE

    async def get_prefix(self):
        if cache["server_prefix"]:
            prefixes = list(cache["servers_prefixes"])
            server_prefix = prefixes[str(self.id)]
        else:
            with open(self.prefixes_filename, "r") as f:
                prefixes = json.load(f)
                cache["servers_prefixes"] = prefixes
                server_prefix = prefixes[str(self.id)]

        return server_prefix

    async def change_prefix(self, ctx, prefix: str):
        if os.path.isfile(self.prefixes_filename):
            with open(self.prefixes_filename, "r") as f:
                prefixes = json.load(f)
            with open(self.prefixes_filename, "w") as f:
                prefixes[str(self.id)] = prefix
                json.dump(prefixes, f, indent=4)
                await ctx.send("Prefix został pomyślnie zmieniony na '{}'".format(prefix))
