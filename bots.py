import discord
from discord.ext import commands
from common import Common

class BotCog(commands.Cog, name="Bot"):

    def __init__(self, bot):
        self.bot = bot

    # Shortcut for showing ALL information. Good command for testing.
    # Same as running !account !node !server !blocks 
    @commands.command(name='show_all', help="Show all information")
    async def show_all(self,ctx):
        try:
            # Show ALL information
            await ctx.invoke(self.bot.get_command('account'))
            await ctx.invoke(self.bot.get_command('node'))
            await ctx.invoke(self.bot.get_command('server'))
            await ctx.invoke(self.bot.get_command('blocks'))
        except Exception as e:
            raise Exception("Exception showing info summary", e)   

    @commands.command(name='invite', help="Displays invite link")
    async def invite(self,ctx):
        try:
            client_id = self.bot.get_client_id()
            permissions = self.bot.get_permission_int()
            response = f"Open a browser and go to https://discord.com/oauth2/authorize?client_id={client_id}&permissions=247872&scope=bot"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Exception generating invite link", e)      

    # Update the command prefix to something new
    @commands.command(name='set_prefix', help="Set bot prefix")
    async def set_prefix(self,ctx,new_prefix=""):
        try:
            # Check that new prefix is valid
            if(new_prefix == ""):
                await ctx.send(f"Usage: {self.bot.command_prefix}set_prefix <new_prefix>")
                return
            # Update command prefix
            self.bot.command_prefix = new_prefix
            # Alert chat that command prefix has been updated
            await ctx.send(f"Set new command prefix to \"{new_prefix}\"")
            # Update bot status message to show new prefix
            await self.bot.update_status()
        except Exception as e:
            raise Exception(f"Could not change command prefix to \"{new_prefix}\"", e)    

    @commands.command(name='set_logging', help="Set logging level")
    async def set_logging(self,ctx,new_level):
        try:
            new_logging_level = int(new_level)
            print("Set new logging level: ", new_logging_level)
            Common.logger.setLevel(new_logging_level)
            await ctx.send(f"Set logging level to {new_logging_level}")
        except Exception as e:
            raise Exception(f"Could not change logging level to {new_logging_level}", e)    

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))