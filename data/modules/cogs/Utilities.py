import discord
from discord.ext import commands
from data.modules.core.core import cache

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ask_role(self, user: discord.User, guild: discord.Guild, role_name: str, role_id: str):
        """Funkcja wysyłająca wiadomość typu embed na skonfigurowany wcześniej kanał do zatwierdzania próśb"""
        emoji_t = "🇹"
        emoji_n = "🇳"
        channel = self.bot.get_channel(cache["servers_settings"][guild.id]["role_confirm_channel"])
        embed = discord.Embed(
            colour=discord.Colour.red()
        )

        embed.set_author(name="Prośba o przyznanie roli")
        embed.add_field(name="Użytkownik:", value="{} ID: {}".format(user.display_name, user.id), inline=False)
        embed.add_field(name="Rola:", value="{} ID: {}".format(role_name, role_id), inline=False)
        message = await channel.send(embed=embed)
        await message.add_reaction(emoji_t)
        await message.add_reaction(emoji_n)

    async def check_for_duplicates(self, user: discord.User, guild: discord.Guild, role_name: str):
        """Funkcja sprawdzająca czy użytkownik nie prosi o tą samą rolę"""
        channel = self.bot.get_channel(cache["servers_settings"][guild.id]["role_confirm_channel"])
        messages = await channel.history().flatten()
        for message in messages:
            message_embeds = message.embeds
            message_embed_dict = message_embeds[0].to_dict()
            username = message_embed_dict["fields"][0]["value"][:-23]
            rolename = message_embed_dict["fields"][1]["value"][:-23]
            if username == user.display_name and rolename == role_name:
                return True

        return False

def setup(bot):
    bot.add_cog(Utilities(bot))
