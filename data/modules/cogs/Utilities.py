import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
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

    @commands.command()
    @has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, description: str = None):
        """Stwórz wiadomość z możliwością wzięcia podanej roli"""
        if ctx.channel.id == cache["servers_settings"][ctx.guild.id]["role_management_channel"]:
            emoji_check = "✅"
            channel = self.bot.get_channel(cache["servers_settings"][ctx.guild.id]["role_announcement_channel"])
            embed = discord.Embed(
                colour=discord.Colour.green()
            )

            embed.set_author(name="Poproś o przyznanie roli {} ID: {}".format(role.name, role.id))
            if description is not None and len(description) <= 150:
                embed.add_field(name="Opis sekcji/grupy:", value="{}".format(description), inline=False)
            elif description is not None and len(description) > 150:
                await ctx.send("Wiadomość przesłana bez opisu\n"
                               "**Powód**\n"
                               "Opis jest za długi! Dopuszczalna długość to 150 znaków")
                embed.remove_field(0)
            message = await channel.send(embed=embed)
            await message.add_reaction(emoji_check)
        else:
            await ctx.send("Tej komendy mogą używać tylko administratorzy!")

        # TODO: Usunięcie tej komendy i wykorzystanie jej mechanizmów do bot.event on_add_reaction

def setup(bot):
    bot.add_cog(Utilities(bot))
