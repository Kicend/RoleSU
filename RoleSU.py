import json
import discord
from discord.ext import commands
from itertools import cycle
from asyncio import sleep as aio_sleep
from data.config import config
from data.modules.core.core import startup
from data.modules.core.core import cache
from data.modules.cogs.Utilities import Utilities

def get_prefix(bot, message):
    with open("data/settings/servers_prefixes/prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix=get_prefix, description="RoleSU wersja {}".format(config.version))
bot.remove_command("help")

async def get_embed_from_msg(reaction, role_announcement_channel, role_confirm_channel=None, switch: int = None):
    if switch == 0:
        msg_confirm = await role_confirm_channel.fetch_message(reaction.message.id)
        message_embeds = msg_confirm.embeds
        msg_embed_dict = message_embeds[0].to_dict()
        name = msg_embed_dict["fields"][1]["value"]
        role_name = name[:-23]
        role_id = name[name.index(":") + 2:]

        return [role_name, role_id]

    elif switch == 1:
        msg_announcement = await role_announcement_channel.fetch_message(reaction.message.id)
        message_embeds = msg_announcement.embeds
        msg_embed_dict = message_embeds[0].to_dict()
        name = msg_embed_dict["author"]["name"]
        role_name = name[name.index("l") + 3:-23]
        role_id = name[name.index(":") + 2:]

        return [role_name, role_id]

@bot.event
async def on_connect():
    print("Bot pomyślnie połączył się z Discordem\nTrwa wczytywanie danych...")
    for cog in config.__cogs__:
        try:
            bot.load_extension(cog)
        except discord.ext.commands.errors.NoEntryPointError:
            print("Nie udało się załadować rozszerzenia {}".format(cog))

@bot.event
async def on_ready():
    print("Zalogowany jako {0} ({0.id})".format(bot.user))
    print("-------------------------------------------------")
    await startup(bot)
    status = cycle(["Monitoruję serwer", "RoleSU {}".format(config.version)])
    while not bot.is_closed():
        current_status = next(status)
        game = discord.Game(current_status)
        await bot.change_presence(status=discord.Status.online, activity=game)
        await aio_sleep(10)

@bot.event
async def on_member_join(member):
    autorole = cache["servers_settings"][member.guild.id]["autorole"]
    if autorole is not None:
        autorole_id = autorole[-18:]
        role = discord.utils.get(member.guild.roles, id=int(autorole_id))
        await member.add_roles(role)

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == "🇳":
        msg_emoji_count = msg.reactions[1].count
    else:
        msg_emoji_count = msg.reactions[0].count
    guild = bot.get_guild(payload.guild_id)

    class Reaction:
        def __init__(self, emoji):
            self.emoji = emoji.name
            self.message = msg
            self.guild = guild
            self.count = msg_emoji_count

    reaction = Reaction(payload.emoji)
    await on_reaction_add(reaction, payload.member)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id not in cache["messages"]:
        cache["messages"][reaction.message.id] = 1
        role_confirm_channel = bot.get_channel(
                               cache["servers_settings"][reaction.message.guild.id]["role_confirm_channel"])
        role_announcement_channel = bot.get_channel(
                                    cache["servers_settings"][reaction.message.guild.id]["role_announcement_channel"])
        guild = reaction.message.guild
        if reaction.emoji == "🇹" and reaction.count > 1 and reaction.message.channel.id == role_confirm_channel.id:
            cache["messages"][reaction.message.id] = 1
            required_info = await get_embed_from_msg(reaction, role_announcement_channel, role_confirm_channel, 0)
            user_dm = await cache["messages"][reaction.message.id]["user"].create_dm()
            role = discord.utils.get(reaction.message.guild.roles,
                                     name=required_info[0])
            try:
                await cache["messages"][reaction.message.id]["user"].add_roles(role)
                await user_dm.send("Rola '{}' została przyznana!".format(required_info[0]))
                channel = bot.get_channel(cache["servers_settings"][reaction.message.guild.id]
                                         ["role_management_channel"])
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )
                embed.set_author(name="DZIENNIK ZDARZEŃ")
                embed.add_field(name="Użytkownik:", value="{} ID: {}".format
                               (cache["messages"][reaction.message.id]["user"].display_name,
                                cache["messages"][reaction.message.id]["user"].id), inline=False)
                embed.add_field(name="Wnioskowana rola:", value="{} ID: {}".format(role.name, role.id), inline=False)
                embed.add_field(name="Zatwierdził:", value="{} ID: {}".format(user.display_name, user.id), inline=False)
                await channel.send(embed=embed)
            except discord.Forbidden:
                await user_dm.send(
                      "Rola '{}' nie została przyznana!".format(required_info[0]))
            try:
                msg = await role_confirm_channel.fetch_message(reaction.message.id)
                await msg.delete()
            except discord.NotFound:
                pass
        elif reaction.emoji == "🇳" and reaction.count > 1 and reaction.message.channel.id == role_confirm_channel.id:
            cache["messages"][reaction.message.id] = 1
            required_info = await get_embed_from_msg(reaction, role_announcement_channel, role_confirm_channel, 0)
            user_dm = await cache["messages"][reaction.message.id]["user"].create_dm()
            role = discord.utils.get(reaction.message.guild.roles,
                                     name=required_info[0])
            try:
                channel = bot.get_channel(cache["servers_settings"][reaction.message.guild.id]
                                          ["role_management_channel"])
                embed = discord.Embed(
                    colour=discord.Colour.blue()
                )
                embed.set_author(name="DZIENNIK ZDARZEŃ")
                embed.add_field(name="Użytkownik:", value="{} ID: {}".format
                (cache["messages"][reaction.message.id]["user"].display_name,
                 cache["messages"][reaction.message.id]["user"].id), inline=False)
                embed.add_field(name="Wnioskowana rola:", value="{} ID: {}".format(role.name, role.id), inline=False)
                embed.add_field(name="Odrzucił:", value="{} ID: {}".format(user.display_name, user.id), inline=False)
                await channel.send(embed=embed)
                msg = await role_confirm_channel.fetch_message(reaction.message.id)
                await msg.delete()
            except discord.NotFound:
                pass
            await user_dm.send("Rola '{}' nie została przyznana!".format(required_info[0]))
        elif reaction.emoji == "✅" and reaction.count > 1 and reaction.message.channel.id == role_announcement_channel.id:
            cache["messages"][reaction.message.id]["user"] = user
            required_info = await get_embed_from_msg(reaction, role_announcement_channel, switch=1)
            utilities_object = Utilities(bot)
            check = await utilities_object.check_for_duplicates(user, reaction.guild, required_info[0])
            if check:
                user_dm = await user.create_dm()
                await user_dm.send("Wysłałeś już jedną prośbę o tą samą rolę! Poczekaj na realizację!")
            else:
                await utilities_object.ask_role(user, guild, required_info[0], required_info[1])
    else:
        del cache["messages"][reaction.message.id]

@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    msg_emoji_count = msg.reactions[0].count
    guild = bot.get_guild(payload.guild_id)
    user = None
    for member in guild.members:
        if member.id == payload.user_id:
            user = member

    class Reaction:
        def __init__(self, emoji):
            self.emoji = emoji.name
            self.message = msg
            self.guild = guild
            self.count = msg_emoji_count

    reaction = Reaction(payload.emoji)
    await on_reaction_remove(reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    role_confirm_channel = bot.get_channel(
                           cache["servers_settings"][reaction.message.guild.id]["role_confirm_channel"])
    role_announcement_channel = bot.get_channel(
                                cache["servers_settings"][reaction.message.guild.id]["role_announcement_channel"])
    if reaction.emoji == "✅" and reaction.message.channel.id == role_announcement_channel.id:
        required_info = await get_embed_from_msg(reaction, role_announcement_channel, role_confirm_channel, 1)
        role = discord.utils.get(reaction.message.guild.roles,
                                 name=required_info[0])
        try:
            await user.remove_roles(role)
        except AttributeError:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nie podałeś wymaganego argumentu")
    elif isinstance(error, commands.CommandInvokeError):
        original = error.original
        if isinstance(original, discord.Forbidden):
            await ctx.send("Nie masz uprawnień do wykonania tej komendy lub Nie mam uprawnień do wykonania tej komendy")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Nie posiadam takiej komendy w swojej bazie danych")
    elif isinstance(error, commands.CommandError):
        error_content = error.args[0]
        if error_content.count("Role") and error_content.count("required"):
            await ctx.send("Nie posiadasz wymaganej roli do wykonania tej komendy!")

bot.run(config.TOKEN)
