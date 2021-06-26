#!/usr/bin/python3

# Nano Discord bot
from pathlib import Path
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import requests
import json
from blocks import BlocksCog
from accounts import AccountsCog
from nodes import NodesCog
from server import ServerCog
from bots import BotCog
from common import Common

class NanoNodeBot(commands.Bot):

    online = True
    discord_token = ""
    rpc_url = ""
    api_url = ""
    client_id = ""
    cmd_prefix = ""
    permission = 0
    timeout = 0

    def __init__(self):
        # Load discord token from .env file
        load_dotenv()
        self.discord_token= os.getenv('discord_token')
        self.rpc_url = os.getenv('rpc_url')
        self.api_url = os.getenv('api_url')
        self.client_id = os.getenv('client_id')
        self.delegators_url = os.getenv('delegators_url')
        self.cmd_prefix = os.getenv('command_prefix', "!")
        self.permission = int(os.getenv('permission', 247872))
        self.timeout = float(os.getenv('timeout', 5.0))
        # Init set command prefix and description
        commands.Bot.__init__(self, command_prefix=self.cmd_prefix,description="Nano Node Bot")
        # Add plug-ins
        self.add_cog(BlocksCog(self))
        self.add_cog(AccountsCog(self))
        self.add_cog(NodesCog(self))
        self.add_cog(ServerCog(self))
        self.add_cog(BotCog(self))

    def run(self):
        # Run bot
        super().run(self.discord_token)
    
    # This is called when the bot has logged on and set everything up
    async def on_ready(self):
        # Log successful connection
        Common.log(f"{self.user.name} connected")
        node_name = await self.get_value('nanoNodeName')
        status = f"Online"
        await self.set_online(True)

    # This is called when the bot sees an unknown command
    async def on_command_error(self, ctx, error):
        Common.log_error(f"{ctx.message.author} tried unknown command {ctx.invoked_with} Error: {error}")
        await ctx.send(f"I do not know what {ctx.invoked_with} means.")

    # This is called when the bot has an error
    async def on_error(self, ctx, error):
        print("Bot encountered error: ", error)
        Common.log_error("Error: {error}")

    # This is called when the bot disconnects
    async def on_disconnect(self):
        print("Bot disconnected")
        # Log successful connection
        Common.log_error(f"{self.user.name} disconnected.")

    # Send RPC request to rpc_url
    async def send_rpc(self, param):
        answer = ""
        try:            
            # sending get request and saving the response as response object
           # r = requests.post(url = self.get_rpc_url(), data = param, timeout=self.timeout)
            data = {"action":"version"}
            r = requests.post("http://localhost:7076", json=data, timeout=self.timeout)
            print("RPC URL: ", self.get_rpc_url())
            print("Param: ", param)
            print("Status code: ", r.status_code)
            print("Answer: ", r.text)
            # If success
            if r.status_code == 200:
                # Parse JSON
                answer = json.loads(r.text)
                # Log answer 
                Common.logger.info(f"<- {answer}")
            else:
                # Update the status to
                await self.set_online(False)
                raise Exception("Could not connect to API")
        except Exception as ex:
            raise ex
        return answer

    # Helper function for getting value from response
    # From MyNanoNinja API endpoint
    async def get_value(self, param):
        answer = ""
        try:
            # Grab response from API_URL
            r = requests.get(self.get_api_url(), timeout=self.timeout)
            if r.status_code == 200:
                # Parse JSON
                content = json.loads(r.text)
                # Grab value named param
                answer = content[param]
                # Log answer 
                Common.logger.info(f"<- {answer}")
                # Update to online
                online = await self.get_online()
                if(online== False):
                    await self.set_online(True)
            else:
                # Update the status to
                await self.set_online(False)
                raise Exception("Could not connect to API")
        except Exception as ex:
            raise ex
        return answer
    
    async def get_delegators(self):
        answer = ""
        try:
            # Grab response from API_URL
            r = requests.get(self.get_delegators_url(), timeout=self.timeout)
            if r.status_code == 200:
                # Parse JSON
                content = json.loads(r.text)

                for item in content:
                    answer = content[item]
  
                for item in answer:
                    answer[item] = (float(answer[item]) / 1000000000000000000000000000000.0)

                # Log answer 
                Common.logger.info(f"<- {answer}")
                # Update to online
                online = await self.get_online()
                if(online== False):
                    await self.set_online(True)
            else:
                # Update the status to
                await self.set_online(False)
                raise Exception("Could not connect to API")
        except Exception as ex:
            raise ex
        return answer

    # Get online status of node
    async def get_online(self):
        return self.online

    # Set online status of node
    async def set_online(self, param):
        try:
            self.online = param
        except Exception as e:
            Common.logger.error("Exception occured updating online status", exc_info=True)
        finally:
            await self.update_status()

    async def update_status(self):
            online = await self.get_online()
            if(online):
                status = f"Online, say {self.command_prefix}help"
            else:
                status = f"Offline, say {self.command_prefix}help"
            # Update bot status
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))

    def get_api_url(self):
        return self.api_url

    def get_rpc_url(self):
        return self.rpc_url
    
    def get_delegators_url(self):
        return self.delegators_url

    def get_client_id(self):
        return self.client_id

    def get_permission_int(self):
        return self.permission

    def get_discord_token(self):
        return self.discord_token

if __name__=='__main__':
    # Initiate Discord bot
    bot = NanoNodeBot()
    bot.run()