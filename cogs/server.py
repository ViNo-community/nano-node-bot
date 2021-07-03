import socket
from discord.ext import commands
from common import Common

class ServerCog(commands.Cog, name="Server"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='server', help="Displays summary of server information")
    async def server(self,ctx):
        try:
            node_name = await self.bot.get_value('nanoNodeName')
            server_load =  await self.bot.get_value('systemLoad')
            usedMem = await self.bot.get_value('usedMem')
            totalMem = await self.bot.get_value('totalMem')
            percent = int(usedMem) / int(totalMem) * 100
            server_uptime = await self.bot.get_value('systemUptime')
            node_uptime = await self.bot.get_value('nodeUptimeStartup')
            pretty_node_uptime = Common.get_days_from_secs(node_uptime)
            server = socket.gethostname()
            ip_addr = socket.gethostbyname(server)
            response = (
                f"**Server:** {server} [{ip_addr}]\n"
                f"**Node Name:** {node_name}\n"
                f"**Server Load:** {server_load}\n"
                f"**Memory Usage:** {usedMem} MB / {totalMem} MB : {percent:.2f}%\n"
                f"**Server Uptime:** {server_uptime}\n"
                f"**Node Uptime:** {pretty_node_uptime}"
            )
            await ctx.send(response)
        except Exception as e:
            raise Exception("Exception displaying server summary", e)      

    @commands.command(name='server_uptime', aliases=['serveruptime','sup'], help="Displays server uptime")
    async def server_uptime(self,ctx):
        try:
            value = await self.bot.get_value('systemUptime')
            response = f"Server uptime is {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab server_uptime", e)      

    @commands.command(name='server_load', aliases=['serverload','systemload','load'], help="Displays server load")
    async def server_load(self,ctx):
        try:
            value = await self.bot.get_value('systemLoad')
            response = f"Server load is {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab server_load", e)           

    @commands.command(name='mem_usage', aliases=['memory_usage','memusage','memory','mem'], help="Displays memory usage")
    async def mem_usage(self,ctx):
        try:
            usedMem = await self.bot.get_value('usedMem')
            totalMem = await self.bot.get_value('totalMem')
            percent = int(usedMem) / int(totalMem) * 100
            response = f"Memory usage is {usedMem} MB / {totalMem} MB : {percent:.2f}%"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab mem_usage", e)      

    @commands.command(name='hostname', aliases=['host'], help="Displays host name")
    async def node_name(self,ctx):
        try:
            value = await self.bot.get_value('nanoNodeName')
            response = f"Node hostname is {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab host name", e)      

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(ServerCog(bot))