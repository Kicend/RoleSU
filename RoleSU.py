import json
import discord
from discord.ext import commands
from data.config import config
from data.modules.core.core import startup
from data.modules.core.core import cache

def get_prefix(bot, message):
    with open("data/settings/servers_prefixes/prefixes.json", "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix=get_prefix, description="RoleSU wersja {}".format(config.version))
bot.remove_command("help")

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
    print("----------------------------------------------")
    await startup(bot)
    current_status = "Monitoruję serwer"
    game = discord.Game(current_status)
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_reaction_add(reaction, user):
    member: discord.Member = cache["waiting_messages"][reaction.message.id][0]
    reports_channel = bot.get_channel(627221454110326785)
    channel = await member.create_dm()
    if reaction.emoji == "🇹" and reaction.message.id in cache["waiting_messages"].keys() and reaction.count > 1:
        role = discord.utils.get(cache["waiting_messages"][reaction.message.id][4],
                                 name=cache["waiting_messages"][reaction.message.id][2])
        await member.add_roles(role)
        await channel.send("Rola '{}' została przyznana!".format(cache["waiting_messages"][reaction.message.id][2]))
        del cache["waiting_messages"][reaction.message.id]
        msg = await reports_channel.fetch_message(reaction.message.id)
        await msg.delete()
    elif reaction.emoji == "🇳" and reaction.message.id in cache["waiting_messages"].keys() and reaction.count > 1:
        msg = await reports_channel.fetch_message(reaction.message.id)
        await msg.delete()
        await channel.send("Rola '{}' nie została przyznana!".format(cache["waiting_messages"][reaction.message.id][2]))
        del cache["waiting_messages"][reaction.message.id]

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
