import discord
from discord.ext import commands
from common import Common
import json 

class AccountsCog(commands.Cog, name="Accounts"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='account', aliases=['acc'], help="Displays summary of account information")
    async def account(self,ctx):
        try:
            account = await self.bot.get_value('nanoNodeAccount')
            representative =  await self.bot.get_value('repAccount')
            balance = await self.bot.get_value('accBalanceMnano')
            pending = await self.bot.get_value('accPendingMnano')
            voting_weight = await self.bot.get_value('votingWeight')
            response = (
                f"**Account:** {account}\n"
                f"**Representative:** {representative}\n"
                f"**Balance:** {balance:.2f} nano\n"
                f"**Pending:**: {pending: .2f} nano\n"
                f"**Voting Weight**: {voting_weight: .2f} nano"
            )
            await ctx.send(response)
        except Exception as e:
            raise Exception("Error showing account summary", e)      

    @commands.command(name='balance', aliases=['bal','show_balance'], help="Displays account balance")
    async def balance(self,ctx):
        try:
            value = await self.bot.get_value('accBalanceMnano')
            response = f"Account balance is {value:.2f} nano"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab balance", e)   

    @commands.command(name='pending', aliases=['show_pending'], help="Displays account pending")
    async def pending(self,ctx):
        try:
            value = await self.bot.get_value('accPendingMnano')
            response = f"Account pending is {value:.2f} nano"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not display account pending", e)     

    @commands.command(name='representative', aliases=['rep','show_rep','show_representative'], help="Displays representative")
    async def representative(self,ctx):
        try:
            value = await self.bot.get_value('repAccount')
            response = f"Representative: {value}"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab representative", e)    

    @commands.command(name='voting_weight', aliases=['votingweight','weight','voting'], help="Displays voting weight")
    async def voting_weight(self,ctx):
        try:
            value = await self.bot.get_value('votingWeight')
            response = f"Voting weight is {value:.2f} nano"
            await ctx.send(response)
        except Exception as e:
            raise Exception("Could not grab voting weight", e)  
    
    @commands.command(name='delegators', aliases=['show_delegators'], help="Displays the delegators of the node")
    async def delegators(self,ctx,ref_account=""):
        try:
            # If no account specified use account of node
            if(ref_account == ""):
                nano_account = await self.bot.get_nano_account()
            else:
                nano_account = ref_account
            value = await self.bot.send_rpc({"action":"delegators","account":nano_account})
            content = json.loads(value)
            # Parse delegators information - account number and balance
            delegators = content['delegators']
            msg = ""
            if(content['delegators'] == ""):
                msg = "No delegators"
            else:
                for item in delegators:
                    msg += "**Account:** " + item + " **Balance:** " + delegators[item] + "\n"
            await ctx.send(msg)
        except Exception as e:
            raise Exception("Could not grab delegators", e)

# Plug-in function to add cog
def setup(bot):
    bot.add_cog(AccountsCog(bot))