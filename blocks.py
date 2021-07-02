import discord
from discord.ext import commands
from common import Common
import random
import requests
from bs4 import BeautifulSoup


class BlocksCog(commands.Cog, name="Blocks"):

    def __init__(self, bot):
        self.bot = bot

    # Hidden Easter Egg command - !meow - shows a random image of a cat
    @commands.command(name='meow',hidden=True)
    async def meow(self,ctx):
        try:
            # Grab google image search results for cat
            page= requests.get('http://www.google.com/search?q=cats&source=lnms&tbm=isch', headers={'User-Agent': 'Mozilla/5.0'})
            # Parse through and grab all the non-gif image links
            soup = BeautifulSoup(page.text, 'html.parser')
            cat_images = []
            for link in soup.find_all('img'):
                src=link.get('src')
                if(not src.endswith('gif')):    # Exclude gifs
                    cat_images.append(src)
            # Grab a random image from the list
            idx = random.randint(0,len(cat_images))
            # Embed the image and share with chat
            imageURL = cat_images[idx]
            embed = discord.Embed()
            embed.set_image(url=imageURL)
            await ctx.send(embed=embed)
        except Exception as e:
            Common.logger.error("Exception occured processing meow request", exc_info=True)
            await ctx.send(ERROR_MESSAGE)    

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