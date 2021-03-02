# Copyright (c) 2020 ShrapGnoll ShrapGnoll@gmail.com
# Subject to MIT license. See LICENSE.md for the full text.

import os, sys, socket
import random, hashlib, time
import asyncio
import logger

class PrismClientProtocolException(Exception):
    """
    PrismClientProtocolException
    """
class PrismClientProtocolConnectionLost(Exception):
    """
    PrismClientProtocolException Connection Lost
    """

class PrismClientProtocol(asyncio.Protocol):
    """
    #  These are callback method overrides for asyncio.Protocol
    """
    def connection_made(self, transport):
        self.logger.log("Connection Established.")
        self.transport = transport

    def connection_lost(self, exc):
        self.authenticated = False
        self.logger.log("PRISM Connection lost. " + str(exc), queue=True)
        raise PrismClientProtocolConnectionLost("PRISM Connection Lost")

    def data_received(self, data):
        if self.debug:
            self.logger.log(b"callback data_received: " + data)
        self.recurse_messages(data.decode())

    def __init__(self, loop, config=None):
        # program loop for asyncio.Protocol
        self.loop = loop
        # this dict assigns subjects to parsers
        self.PARSERS = {"login1": self._h_login1,       "errorcritical": self._h_log,
                        "error": self._h_log,           "connected": self._h_connected,
                        "raconfig": self._h_donothing,  "chat": self._h_chat,
                        "kill": self._h_kill,           "success": self._h_success,
                        "APIAdminResult": self._h_log_and_queue, "serverdetails": self._h_serverdetails}
        self.GAME_MANANGEMENT_CHAT = ["Game", "Admin Alert", "Response"]
        # net
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ""
        self.port = 4712
        self.input_buffer = ""
        self.output_buffer = []
        self.transport = None
        # credentials
        self.username = ""
        self.password_hash = ""
        self.client_challenge = ""
        self.server_challenge = ""
        self.salt = ""
        # program state
        self.config = None
        self.authenticated = False
        self.debug = False # Toggle this to see detailed output
        self.logger = logger.Logger()
        self.periodic = [self.periodic_showafk]
        self.showafk = 1200
        if config:
            self.host = config["PRISM"]["HOST"]
            self.port = config["PRISM"]["PORT"]
            self.username = config["PRISM"]["USERNAME"]
            self.password = config["PRISM"]["PASSWORD"]
            self.showafk = int(config["PRISM"]["SHOWAFK"])
            self.config = config

    def recurse_messages(self, data):
        DELIMIT = "\4\0"  # raw protocol msg delimiter
        if self.input_buffer:  # update from the buffer
            data = self.input_buffer + data
            self.clear_input_buffer()  # clear the buffer after retrieval
        msgs = data.split(DELIMIT, 1)  # this chomps 1 message and stores the rest [m1, m2\4\0m3\4\0m4...]
        if DELIMIT in data and msgs[1] == "":  # only 1 complete message
            self.parse_command(msgs[0])
        elif DELIMIT not in data:  # only incomplete data
            self.set_input_buffer(data)
        elif DELIMIT in data and DELIMIT not in msgs[1]:  # 1 message and incomplete data
            self.parse_command(msgs[0])
            self.set_input_buffer(msgs[1])
        elif DELIMIT in data and DELIMIT in msgs[1]:  # more than 1 complete message
            self.parse_command(msgs[0])
            self.recurse_messages(msgs[1])  # recursively parse other messages

    def parse_command(self, command):
        found = False
        for subj in self.PARSERS:
            if subj in command[:1 + len(subj)]:
                self.PARSERS[subj](command)
                found = True
                break
        if self.debug and not found:  # log messages with no parser if debug is True
            self._h_log("No parser found: " + command)

    def set_input_buffer(self, data):
        self.input_buffer = data

    def clear_input_buffer(self):
        self.input_buffer = ""

    def _send_output_buffer(self):
        if not self.transport:
            self.logger.log("Transport not ready!")
            return
        while self.output_buffer:
            data = self.output_buffer.pop(0)  # fifo queue
            if self.debug:
                self.logger.log(b"\nasyncio transport.write " + data)
            self.transport.write(data)

    def send_command(self, *args):
        """
        run a command on PRISM, args should be a list like ["setnext", "kashan", "cq", "std"]
        """
        self._raw_send_command("apiadmin", *args)
        # TODO TODO

    def _raw_send_command(self, subject, *args):
        data = str("\1" + subject + "\2" + "\3".join(args) + "\4\0")
        self.output_buffer.append(data.encode())
        self._send_output_buffer()

    def get_server_details(self):
        self._raw_send_command("serverdetailsalways")

    def set_logger(self, log_instance):
        self.logger = log_instance

    @staticmethod
    def auth_digest(username, password_hash, salt, client_challenge, server_challenge):
        salted_hash = hashlib.sha1(str(salt + "\1" + password_hash).encode()).hexdigest()
        return hashlib.sha1("\3".join([username, client_challenge, server_challenge, salted_hash]).encode()).hexdigest()

    def login(self, username, password):
        if self.authenticated:
            self.logger.log("PRISM already authenticated.", queue=True)
            return
        self.logger.log("Attempting login.", queue=True)
        csprng = random.SystemRandom()
        self.username = username
        self.password_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
        self.client_challenge = hex(csprng.getrandbits(128)).lstrip("0x").rstrip("L")
        self._raw_send_command("login1", "1", self.username, self.client_challenge)

    async def periodic_showafk(self):
        while True:
            await asyncio.sleep(self.showafk)
            self._raw_send_command("say", "!showafk")

    """
    ## Subject Handlers ##
    """

    def _h_login1(self, data):
        self.salt, self.server_challenge = data[len("\1login1\2"):].split("\3")
        if self.salt and self.server_challenge:
            self._h_login2()
        else:
            self.logger.log("Failed login bad salt or server challenge.")

    def _h_login2(self):
        self._raw_send_command("login2", self.auth_digest(
            self.username,
            self.password_hash,
            self.salt,
            self.client_challenge,
            self.server_challenge))
        self.password_hash = ""  # don't store this credential long
        self.client_challenge = ""  # clear client chal because its a nonce

    def _h_connected(self, data):
        self.authenticated = True
        self._h_log(data)

    def _h_chat(self, data):
        spl = data.split("\3")
        if len(spl) < 3:
            self._h_log(data)
        elif spl[2] in self.GAME_MANANGEMENT_CHAT:
            if spl[2] == "Admin Alert":
                self._h_squelch(data, self.config["SQUELCH_ADMIN"])
            elif spl[2] == "Game":
                self._h_squelch(data, self.config["SQUELCH_GAME"])
            else:
                self._h_log(data, queue=True)
        else:
            self._h_log(data)

    def _h_squelch(self, data, squelch_list):
        """
        Only log data if it does not contain any strings listed in squelch_list
        """
        for msg in squelch_list:
            if squelch_list[msg] in data:
                return
        self._h_log(data, queue=True)

    def _h_log_and_queue(self, data):
        self._h_log(data, queue=True)

    def _h_log(self, data, queue=False):
        try:
            prefix_split = data.split("\2")
            msg_split = prefix_split[1].split("\3")
            self.logger.log(" ".join(msg_split[2:]), queue=queue)
        except IndexError:
            self.logger.log(data, queue=queue)

    def _h_success(self, data):
        self._h_log(data, queue=True)

    def _h_donothing(self, data):
        pass

    def _h_kill(self, data):
        pass

    def _h_serverdetails(self, data):
        """
        parses serverdetails messages into a dict
        """
        try:
            msg = data.split("\2")[1].split("\3")
            details = {
                "serverName": msg[0],
                "serverIP": msg[1],
                "serverPort": msg[2],
                "serverStartupTime": msg[3],
                "serverWarmup": msg[4],
                "serverRoundLength": msg[5],
                "maxPlayers": msg[6],
                "status": msg[7],
                "map": msg[8],
                "mode": msg[9],
                "layer": msg[10],
                "timeStarted": msg[11],
                "players": msg[12],
                "team1": msg[13],
                "team2": msg[14],
                "tickets1": msg[15],
                "tickets2": msg[16],
                "rconUsers": msg[17]
            }
            details_str = ""
            for pair in details.items():
                details_str += str(pair[0]) + " : " + str(pair[1]) + "\n"
            self.logger.log(details_str, queue=True)
        except IndexError:
            self.logger.log("Failed to parse serverdetails.", queue=True)


