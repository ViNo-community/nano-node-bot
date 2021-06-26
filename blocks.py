import discord
from discord.ext import commands
from common import Common

class BlocksCog(commands.Cog, name="Blocks"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='blocks', help="Displays summary of block information")
    async def block(self,ctx):
        try:
            currentBlock = await self.bot.get_value('currentBlock')
            cementedBlocks = await self.bot.get_value('cementedBlocks')
            uncheckedBlocks = await self.bot.get_value('uncheckedBlocks')
            sync = await self.bot.get_value('blockSync')
            response = (
                f"**Cemented Blocks:** {cementedBlocks}\n"
                f"**Current Block:** {currentBlock}\n"
                f"**Unchecked Blocks:** {uncheckedBlocks}\n"
                f"**Sync:**: {sync}%\n"
            )
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab blocks", e)       

    @commands.command(name='current_block', aliases=['currentblock','cur','current'], help="Displays the current block")
    async def current_block(self,ctx):
        try:
            value = await self.bot.get_value('currentBlock')
            response = f"Current block is {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab current_block", e)     

    @commands.command(name='cemented_blocks', aliases=['cementedblocks','cemented','cem'], help="Displays the cemented block count")
    async def cemented_blocks(self,ctx):
        try:
            value = await self.bot.get_value('cementedBlocks')
            response = f"Cemented block count is {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab cemented_blocks", e)  

    @commands.command(name='unchecked_blocks', aliases=['uncheckedblocks','unchecked'], help="Displays the number of unchecked blocks")
    async def unchecked_blocks(self,ctx):
        try:
            value = await self.bot.get_value('uncheckedBlocks')
            response = f"{value} unchecked blocks"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab unchecked blocks", e)   

    @commands.command(name='sync', aliases=['blocksync','block_sync','bsync'], help="Displays block sync")
    async def block_sync(self,ctx):
        try:
            value = await self.bot.get_value('blockSync')
            response = f"Block sync is {value}%"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab sync", e)  

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(BlocksCog(bot))