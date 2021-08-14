#!/usr/bin/python3

# Nano Discord bot
import asyncio
from asyncio.tasks import sleep
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import requests
import json
from common import Common
from threading import Thread
import time

class NanoNodeBot(commands.Bot):

    # Default values
    initialized = False
    online = True
    # The nano account associated with this node
    nano_account = ""
    discord_token = ""
    rpc_url = ""
    api_url = ""
    client_id = ""
    cmd_prefix = "!"
    permission = 0
    timeout = 5.0
    # Check heartbeat every HEARTBEAT_INTERVAL seconds
    heartbeat_interval = 0

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
        self.api_url = os.getenv('api_url')
        self.client_id = os.getenv('client_id')
        self.delegators_url = os.getenv('delegators_url')
        self.cmd_prefix = os.getenv('command_prefix', "!")
        self.permission = int(os.getenv('permission', 247872))
        self.heartbeat_interval = int(os.getenv('heartbeat_interval', 180))
        self.timeout = float(os.getenv('timeout', 5.0))
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
                online = False
                try:
                    # Ping to check if online
                    online = await self.check_online_status()
                except Exception as error:
                    online = False
                    # Error. Output to chat?
                    Common.log_error(f"Error checking online status of node: {error}")
                    print(error)
                print(f"CHECKING IF ONLINE: {online} INIT: {self.initialized}")
                if(self.initialized):
                    await self.set_online(online)
                # Sleep HEARTBEAT_INTERVAL seconds
                time.sleep(self.heartbeat_interval)
        # Start the heartbeat
        heartbeat = Thread(target=asyncio.run, args=(_heartbeat_loop(),))
        heartbeat.daemon = True
        heartbeat.start()
        # Automatically load cogs
        for file in os.listdir('./cogs'):
            if file.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                    Common.log(f"Loaded Cog: {file}")
                    print(f"Loaded: {file}")
                except Exception as e:
                    Common.log_error(f"Could not load Cog: {file}: {e}")
                    print(f"Could not load: {file}:", e)

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
        # Set bot as initialized
        self.initialized = True
        # Log successful connection
        Common.log(f"{self.user.name} connected")
        print(f"{self.user.name} connected")
        await self.set_online(True)

    # Bot encounters an error during command execution
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            Common.logger.error(f"{ctx.message.author} tried unknown command \"{ctx.invoked_with}\" Error: {error}", exc_info=True)
            await ctx.send(f"I do not know what \"{ctx.invoked_with}\" means.")
        elif isinstance(error, ConnectionError):
            Common.logger.error(f"Connection Error: {error}", exc_info=True)
            await ctx.send(f"Connection Error executing command \"{ctx.invoked_with}\". Please check logs")
        elif isinstance(error, commands.CheckFailure):
            Common.logger.error(f"Check Failure Error: {error} {error.args}", exc_info=True)
            await ctx.reply(f"Sorry, you do not have permission to execute \"{ctx.invoked_with}\".")    
        else:
            Common.logger.error(f"Error: {error}", exc_info=True)
            await ctx.send(f"Error executing command \"{ctx.invoked_with}\". Please check logs.")
 

    # This is called when the bot disconnects
    async def on_disconnect(self):
        print("Bot disconnected")
        # Log successful connection
        Common.log_error(f"{self.user.name} disconnected.")

    # Send RPC request to rpc_url
    async def send_rpc(self, param, value=""):
        try:            
            # Send RPC POST request
            Common.logger.info(f"-> {param}");
            r = requests.post(url = self.get_rpc_url(), json=param, timeout=self.timeout)
            # Debug info
            Common.logger.info(f"<- {r.text}")
            # If success
            if r.status_code == 200:
                if(value==""):
                    return r.text
                else:
                    # Parse JSON
                    values = json.loads(r.text)
                    return values[value]
            else:
                # Update the status to
                await self.set_online(False)
                raise Exception("Could not connect to API")
        except KeyError as keyex:
            return ""
        except Exception as ex:
            raise ex

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

    # Get nano account associated with node
    async def get_nano_account(self):
        return await self.get_value('nanoNodeAccount')

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
        return self.api_url

    def get_rpc_url(self):
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