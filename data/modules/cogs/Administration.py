import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.modules.core import core as cr

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix: str):
        server = self.bot.get_guild(ctx.guild.id)
        if server.id not in cr.cache["server_parameters"]:
            cr.cache["server_parameters"][server.id] = cr.GuildParameters(server.id)
        current_prefix = await cr.cache["server_parameters"][server.id].get_prefix()
        if prefix == current_prefix:
            await ctx.send("Już jest ustawiony taki prefix!")
        elif len(prefix) > 5:
            await ctx.send("Ten prefix jest za długi! Maksymalna długość prefixu to 5 znaków!")
        else:
            await cr.cache["server_parameters"][server.id].change_prefix(ctx, prefix)

    @commands.command()
    @has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role, description: str = None):
        """Stwórz wiadomość z możliwością wzięcia podanej roli"""
        if ctx.channel.id == cr.cache["servers_settings"][ctx.guild.id]["role_management_channel"]:
            emoji_check = "✅"
            channel = self.bot.get_channel(cr.cache["servers_settings"][ctx.guild.id]["role_announcement_channel"])
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
    bot.add_cog(Administration(bot))
