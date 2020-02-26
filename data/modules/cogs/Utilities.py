import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.modules.core.core import cache

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, description: str = None):
        """Stwórz wiadomość z możliwością wzięcia podanej roli"""
        if ctx.channel.id == 682303163755266058:
            emoji_check = "✅"
            channel = self.bot.get_channel(cache["servers_settings"][ctx.guild.id]["role_announcement_channel"])
            embed = discord.Embed(
                colour=discord.Colour.green()
            )

            embed.set_author(name="Poproś o przyznanie roli {}".format(role.name))
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

    @commands.command()
    async def ask_role(self, ctx, role: discord.Role):
        """Poproś o rolę"""
        if (ctx.author, ctx.author.id, role.name, role.id) in cache["waiting_messages"].values():
            await ctx.send("Twoja poprzednia prośba nie została jeszcze rozpatrzona!\n"
                           "Prosimy o cierpliwość")
        else:
            emoji_t = "🇹"
            emoji_n = "🇳"
            channel = self.bot.get_channel(681813852312436756)
            embed = discord.Embed(
                colour=discord.Colour.red()
            )

            embed.set_author(name="Prośba o przyznanie roli")
            embed.add_field(name="Użytkownik:", value="{} ID: {}".format(ctx.author, ctx.author.id), inline=False)
            embed.add_field(name="Rola:", value="{} ID: {}".format(role.name, role.id), inline=False)
            message = await channel.send(embed=embed)
            message_id_user_info = {message.id: (ctx.author, ctx.author.id, role.name, role.id, ctx.guild.roles)}
            cache["waiting_messages"].update(message_id_user_info)
            await message.add_reaction(emoji_t)
            await message.add_reaction(emoji_n)
            print(cache["waiting_messages"])

        # TODO: Usunięcie tej komendy i wykorzystanie jej mechanizmów do bot.event on_add_reaction

def setup(bot):
    bot.add_cog(Utilities(bot))
