#!/usr/bin/python3

# Nano Discord bot
import asyncio
from asyncio.tasks import sleep
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
from threading import Thread
import time

class NanoNodeBot(commands.Bot):

    # Default values
    online = True
    discord_token = ""
    rpc_url = ""
    server_name = "patrola.me"
    client_id = ""
    cmd_prefix = "!"
    timeout = 5.0
    # Check heartbeat every HEARTBEAT_INTERVAL seconds
    HEARTBEAT_INTERVAL = 20

    def __init__(self):
        # Load discord token from .env file
        load_dotenv()
        # Check required variables
        if os.getenv('discord_token') is None:
            raise ValueError("DISCORD_TOKEN not found. Could not start bot.")
        if os.getenv('client_id') is None:
            raise ValueError("CLIENT_ID not found. Could not start bot.")
        if os.getenv('rpc_url') is None:
             raise ValueError("RPC_URL not found. Could not start bot.")
        # Grab tokens
        self.discord_token= os.getenv('discord_token')
        self.rpc_url = os.getenv('rpc_url')
        # self.server_name = os.getenv('server')
        self.client_id = os.getenv('client_id')
        if os.getenv('command_prefix') is not None:
            self.cmd_prefix = os.getenv('command_prefix')
        if os.getenv('timeout') is not None:
            try:
                self.timeout = float(os.getenv('timeout') or 5.0)
            except ValueError:
                self.timeout = 5.0
        # Init set command prefix and description
        commands.Bot.__init__(self, command_prefix=self.cmd_prefix,description="Nano Node Bot")
        # Register heartbeat checker
        async def _heartbeat_loop():
            while(True):
                try:
                    # Ping to check if online
                    online = await self.check_online_status()
                    print(f"CHECKING IF ONLINE: {online}")
                   # await self.set_online(online)
                except Exception as error:
                    print(error)
                    #await self.set_online(False)
                # Sleep XXX seconds
                time.sleep(self.HEARTBEAT_INTERVAL)
        # Start the heartbeat
        heartbeat = Thread(target=asyncio.run, args=(_heartbeat_loop(),))
        heartbeat.daemon = True
        heartbeat.start()
        # Add plug-ins
        self.add_cog(BlocksCog(self))
        self.add_cog(AccountsCog(self))
        self.add_cog(NodesCog(self))
        self.add_cog(ServerCog(self))
        self.add_cog(BotCog(self))

    def run(self):
        # Run bot
        super().run(self.discord_token)

    # Check if the nano node is online or not
    async def check_online_status(self):
        # NOTE: This can be done a better way once it has direct access to RPC.
        # Grab response from API_URL
        r = requests.get(self.get_api_url(), timeout=self.timeout)
        if r.status_code == 200:
            return True
        else:
            return False

    # This is called when the bot has logged on and set everything up
    async def on_ready(self):
        # Log successful connection
        Common.log(f"{self.user.name} connected")
        print(f"{self.user.name} connected")
        node_name = await self.get_value('nanoNodeName')
        status = f"Online"
        await self.set_online(True)


    # This is called when the bot sees an unknown command
    async def on_command_error(self, ctx, error):
        print("Bot encountered command error")
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

    # Helper function for getting value from response
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
                print(f"Got status {r.status_code} !!!!")
                # Update the status to
                await self.set_online(False)
                raise Exception(f"Status {r.status_code}. Could not connect to API")
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
            online = 'Online' if await self.get_online() else 'Offline'
            status = f" say {self.command_prefix}help | {online}"
            # Update bot status
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))

    def get_api_url(self):
        return self.rpc_url

    def get_client_id(self):
        return self.client_id

    def get_permission_int(self):
        return self.permission

    def get_discord_token(self):
        return self.discord_token

if __name__=='__main__':
    # Initiate Discord bot
    try:
        bot = NanoNodeBot()
        print("Bot is now running with prefix " + bot.command_prefix)
        # Run the bot loop
        bot.run()
    except Exception as ex:
        print(f"ERROR: {ex}")
        exit(0)