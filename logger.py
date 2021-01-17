# Copyright (c) 2020 ShrapGnoll ShrapGnoll@gmail.com
# Subject to MIT license. See LICENSE.md for the full text.

import sys
import asyncio
import logging

class Logger:
    def __init__(self, syslog=False, queuelen=200):
        self.log_buffer = []
        self.queuelen = queuelen

    def consume_log(self):
        try:
            return self.log_buffer.pop(0)
        except IndexError:
            return

    def log(self, msg, queue=False, flush=True):
        if not msg:
            return
        msg = str(msg)
        if len(self.log_buffer) > self.queuelen:  # set sane limit
            self.log_buffer = self.log_buffer[self.queuelen:]
        if queue:
            self.log_buffer.append(msg)
        if msg[-1] != "\n":  # ensure last char is \n
            msg = msg + "\n"
        sys.stderr.write(msg, flush=flush)


