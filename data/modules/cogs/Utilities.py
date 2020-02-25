import discord
from discord.ext import commands
from data.modules.core.core import cache

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ask_role(self, ctx, role: discord.Role):
        """Poproś o rolę"""
        if (ctx.author, ctx.author.id, role.name, role.id) in cache["waiting_messages"].values():
            await ctx.send("Twoja poprzednia prośba nie została jeszcze rozpatrzona!\n"
                           "Prosimy o cierpliwość")
        else:
            emoji_t = "🇹"
            emoji_n = "🇳"
            channel = self.bot.get_channel(627221454110326785)
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

def setup(bot):
    bot.add_cog(Utilities(bot))
