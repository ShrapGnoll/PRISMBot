# Project Reality PRISM Discord Bot

A bot to allow admins to read reports and run PRISM commands from your discord server.

## How to use

#### Setting up Discord

This code allows you to run your own Discord bot. You need to make your own Discord Application rather than use an
existing bot. Luckily this process is very easy.

Sign in to the Discord Developer Portal with your discord account.
https://discord.com/developers/applications

Hit 'Create Application' and name your Application. Something like "PR Discord PRISMBot"\
(You will add the bots Discord username later.)

Now you need to grant the bot permission to access your server.

In the settings window on the left, select 'OAuth2' and scroll down a bit.

Under 'Scopes' check 'bot' and under 'Bot Permissions' check 'Read Message History' and 'Send Messages'.

Now copy the URL in the 'Scopes' box and paste it into your browser. This will present a window allowing you to grant
the bot entry to your Discord server.

Take note of the token generated in the "Bot" tab on the left side of your screen. You will need this for the next step.

#### PRISMBot Configuration.

Add a PRISM user to your PRISM configuration, the bot will use this user. 

Download a copy of PRISMBot from github and extract it on the server you want
to run it from, this doesn't have to be the same server PR is hosted on.

<todo link>

Open config.ini in your favorite text editor.

[PRISM]

USERNAME and PASSWORD are the username and password of the PRISM user you set up for the bot.
HOST is the ip address of your PR server (the IP normal PRISM users users use)
Similarly PORT is the PRISM port of your PR server.

[DISCORD]

OWNER_ID is the Discord user ID of the owner, this user will get @mention alerts from the bot.

Note: you will need to turn on Discord developer mode to access user/channel ID
https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

TOKEN this is a secret token you noted down above, from the "Bot" section of your Discord application
DO NOT SHARE THIS TOKEN! It allows control of the bot.
https://discord.com/developers/applications

[DISCORD_CHANNELS]

Adding Discord channel IDs under this section adds a 'command' channel to the bot. Messages will bes

[DISCORD_ADMINS]

This is an **optional** section, if you add the Discord IDs under this section
ONLY those specified will be authorized to run commands with the bot. This might be useful
if you want some admins to have read only access.

[SQUELCH_ADMIN] and [SQUELCH_GAME]

DO NOT NEED TO BE EDITED. They are internal settings and do not need to be touched.
Note for programmers: adding a strings under this section will suppress Game and Admin messages
containing that substring.





