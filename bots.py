import discord
from discord.ext import commands
from common import Common
from common import ERROR_MESSAGE

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
            Common.logger.error("Exception occured processing request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)  

    @commands.command(name='invite', help="Displays invite link")
    async def invite(self,ctx):
        try:
            client_id = self.bot.get_client_id()
            permissions = self.bot.get_permission_int()
            response = f"Open a browser and go to https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot"
            await ctx.send(response)
        except Exception as e:
            Common.logger.error("Exception occured processing request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)    

    @commands.command(name='set_prefix', help="Set bot prefix")
    async def set_prefix(self,ctx,new_prefix):
        try:
            print("Set new command prefix: ",new_prefix)
            self.bot.command_prefix = new_prefix
            await ctx.send(f"Set new command prefix to \"{new_prefix}\"")
        except Exception as e:
            Common.logger.error("Exception occured processing request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)  

    @commands.command(name='set_logging', help="Set logging level")
    async def set_logging(self,ctx,new_level):
        try:
            new_logging_level = int(new_level)
            print("Set new logging level: ", new_logging_level)
            Common.logger.setLevel(new_logging_level)
            await ctx.send(f"Set logging level to {new_logging_level}")
        except Exception as e:
            Common.logger.error("Exception occured processing request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)  

    # THIS TEMPORARY COMMAND IS ONLY FOR DEBUGGING. WILL BE REMOVED
    @commands.command(name='toggle_online', aliases=['toggle'], help="Toggle online status on/off")
    async def toggle_online(self,ctx):
        try:
            isOnline = await self.bot.get_online()
            if(isOnline):
                await ctx.send(f"Bot is online. Turning offline.")
                await self.bot.set_online(False)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Node Offline'))
            else:
                await ctx.send(f"Bot is offline. Turning online.")
                await self.bot.set_online(True)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Node Online'))
        except Exception as e:
            Common.logger.error("Exception occured processing request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)  

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BotCog(bot))