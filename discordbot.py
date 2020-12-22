import sys
import string
import asyncio
import discord
import prismbot
import logger
import random

class DiscordBot(discord.Client):
    def __init__(self, config=None):
        super().__init__()
        self.COMMAND_CHANNELS = []  # channels the bot will accept commands in
        self.OWNER_ID = None  # the owner of the bot, used for informational @mentions
        self.ADMINS = []  # if this list is populated only users listed can run commands
        self.prism_bot = None  # to be assigned to a PrismClientProtocol instance
        self.logger = logger.Logger()
        self.config = None  # configparser ini gets read into here
        self.periodic = [self.log_to_discord, self.status_reconnect, self.status_daily]
        if config:
            self.set_owner(int(config["DISCORD"]["OWNER_ID"]))
            for channel in config["DISCORD_CHANNELS"]:
                self.add_command_channel(int(config["DISCORD_CHANNELS"][channel]))
            for admin in config["DISCORD_ADMINS"]:
                self.add_admin(int(admin))
            self.config = config

    async def on_ready(self):
        await self.log_to_command_channels("PRISMBot Online.")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id not in self.COMMAND_CHANNELS:
            return
        if self.ADMINS and message.author.id not in self.ADMINS:
            await message.channel.send("You are not authorized to send commands over Discord.")
            self.logger.log("Unauthorized user: " + message.author.name + " tried to send command: " + message.content)
            return
        if message.content[0] == "!":  # game command
            msg = message.content[1:].split(" ")
            if self.prism_bot:
                if not msg[1:]:
                    msg_fix = message.content.split(" ")
                    self.prism_bot._raw_send_command("say", *msg_fix)  # TODO fix
                else:
                    self.prism_bot._raw_send_command(msg[0], *msg[1:])
                log_cmd = "User: <@" + str(message.author.id) + "> ran command: " + str(message.content)
                self.logger.log(log_cmd, queue=False)
                await message.channel.send(log_cmd)
            else:
                self.logger.log("PRISMBot not ready", queue=True)
        elif message.content[0] == "/":  # internal command
            if message.content[1:].lower() == "status":
                await message.channel.send("Connected: " + str(self.prism_bot.authenticated))
            if message.content[1:].lower() in ["connect", "login"]:
                self.prism_bot.login(self.prism_bot.username, self.prism_bot.password)

    async def log_to_command_channels(self, msg):
        for id in self.COMMAND_CHANNELS:
            channel = self.get_channel(id)
            await channel.send(msg)

    @staticmethod
    def log_formatter(log):
        if not log:
            return log
        elif log.startswith("Game"):
            return """```css\n""" + log + """```"""
        elif log.startswith("Admin Alert"):
            return """```css\n[ """ + log + """]```"""
        elif log.startswith("Response"):
            return """```fix\n""" + log + """```"""
        else:
            return log

    async def log_to_discord(self):
        while True:
            await asyncio.sleep(1)
            while self.logger.log_buffer:
                data = self.logger.consume_log()
                if not data:
                    return
                await self.log_to_command_channels(self.log_formatter(data))

    async def status_reconnect(self):
        while True:
            await asyncio.sleep(3600*8)  # check every 8 hours
            if not self.prism_bot.authenticated:
                await self.log_to_command_channels("Lost PRISM Connection! <@" + str(self.OWNER_ID) + ">")

    async def status_daily(self):
        while True:
            await asyncio.sleep(3600*24)  # check status every 24 hours
            await self.print_status()

    async def print_status(self):
        if self.prism_bot.authenticated:
            await self.log_to_command_channels("Status: Authenticated.")
        else:
            await self.log_to_command_channels("Status: Disconnected!")

    def set_owner(self, user_id):
        assert (isinstance(user_id, int) or isinstance(user_id, float))
        self.OWNER_ID = user_id

    def add_admin(self, user_id):
        assert (isinstance(user_id, int) or isinstance(user_id, float))
        self.ADMINS.append(user_id)

    def add_command_channel(self, channel_id):
        assert (isinstance(channel_id, int) or isinstance(channel_id, float))
        self.COMMAND_CHANNELS.append(channel_id)

    def assign_bot(self, bot):
        assert isinstance(bot, prismbot.PrismClientProtocol)
        self.prism_bot = bot
