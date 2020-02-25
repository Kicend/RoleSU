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

def setup(bot):
    bot.add_cog(Administration(bot))
