# Copyright (c) 2020 ShrapGnoll ShrapGnoll@gmail.com
# Subject to MIT license. See LICENSE.md for the full text.

import sys
import string
import asyncio
import discord
import prismbot
import logger
import random

class DiscordBot(discord.Client):
    # All default maps - Generate using PRBuild -> Tools -> Generate Maplist

    MAPLISTALL = []  # pending release

    def __init__(self, config=None):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.COMMAND_CHANNEL = None  # channels the bot will accept commands in
        self.TEAMKILL_CHANNEL = None  # channels the bot will print tks in
        self.OWNER_ID = None  # the owner of the bot, used for informational @mentions
        self.ADMINS = []  # if this list is populated only users listed can run commands
        self.prism_bot = None  # to be assigned to a PrismClientProtocol instance
        self.logger = logger.Logger()
        self.config = None  # configparser ini gets read into here
        self.periodic = [self.log_to_discord, self.status_reconnect, self.status_daily]
        if config:
            self.OWNER_ID = int(config["DISCORD"]["OWNER_ID"])
            self.COMMAND_CHANNEL = int(config["DISCORD_CHANNELS"]["COMMAND"])
            self.TEAMKILL_CHANNEL = int(config["DISCORD_CHANNELS"]["TEAMKILL"])
            for admin in config["DISCORD_ADMINS"]:
                self.add_admin(config["DISCORD_ADMINS"][admin])
            self.config = config

    def construct_maplist(self, mode):
        layer_weights = {
            "std": 4,
            "alt": 4,
            "lrg": 3,
            "inf": 2 }
        maplist = set()
        for each in self.MAPLISTALL:
            if each[1] != mode:
                continue
            if each[0] in maplist:
                continue
            map_firstname = each[0].split("_")[0]
            if map_firstname in self.prism_bot.last_maps:
                continue
            maplist.add((each, layer_weights[each[2].lower()]))
        return [choice[0][0] for choice in random.sample(maplist, [each[1] for each in maplist], k=3)]

    async def automvote(self, mode):
        maps = self.construct_maplist(mode)
        await self.prism_bot._raw_send_command("say", "!history")  # gets history into prismbot.last_maps
        await self.prism_bot._raw_send_command("mapvote", *maps)

    async def on_ready(self):
        await self.log_to_command_channel("PRISMBot Online.")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != int(self.COMMAND_CHANNEL):
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
            if message.content[1:].lower() == "serverdetails":
                self.prism_bot.get_server_details()
            if message.content[1:].lower() == "autovote aas":
                await self.automvote("gpm_cq")
            if message.content[1:].lower() == "autovote ins":
                await self.automvote("gpm_insurgency")

    async def log_to_command_channel(self, msg):
        channel = self.get_channel(self.COMMAND_CHANNEL)
        await channel.send(msg)

    @staticmethod
    def log_formatter(log):  # TODO optimize
        strmap = {
            "Game": """```cs\n'\n""" + log + """'```""",
            "Admin Alert": """```diff\n- """ + log + """``` """,
            "Response": """```fix\n""" + log + """```""",
            "serverName :": """```yaml\n""" + log + """```""",
            "Success": """```diff\n+ """ + log + """```"""
        }
        if not log:
            return log
        for prefix in strmap:
            if log.startswith(prefix):
                return strmap[prefix]
        return log

    async def log_to_discord(self):
     while not self.is_ready():    # wait until clinet is ready to 
        await asyncio.sleep(0.5)
        
     while True:
        await asyncio.sleep(0.5)
        while len(self.logger.log_buffer) != 0:
            data = self.logger.consume_log()
            if data[1] is not None:
                channel = self.get_channel(data[1])
                await channel.send(str(data[0]))
            else:
                await self.log_to_command_channel(self.log_formatter(data[0]))

    async def status_reconnect(self):
        while True:
            await asyncio.sleep(3600*8)  # check every 8 hours
            if not self.prism_bot.authenticated:
                await self.log_to_command_channel("Lost PRISM Connection! <@" + str(self.OWNER_ID) + ">")

    async def status_daily(self):
        while True:
            await asyncio.sleep(3600*24)  # check status every 24 hours
            await self.print_status()

    async def print_status(self):
        if self.prism_bot.authenticated:
            await self.log_to_command_channel("Status: Authenticated.")
        else:
            await self.log_to_command_channel("Status: Disconnected!")

    def add_admin(self, user_id):
        if user_id.isnumeric():
            self.ADMINS.append(int(user_id))
        else :
            raise Exception(f"admin id contains charectars : {user_id} ")

    def assign_bot(self, bot):
        assert isinstance(bot, prismbot.PrismClientProtocol)
        self.prism_bot = bot
