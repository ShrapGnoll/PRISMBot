import asyncio
import time
import prismbot
import discordbot
import configparser


async def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    dbot = discordbot.DiscordBot(config=config)
    loop = asyncio.get_running_loop()  # asyncio OS thread loop
    on_con_lost = loop.create_future()  # This is the Future for the program loop
    transport, protocol = await loop.create_connection(lambda: prismbot.PrismClientProtocol(on_con_lost, config),
                                                       config["PRISM"]["HOST"], config["PRISM"]["PORT"])
    dbot.assign_bot(protocol)  # assign PRISM bot to Discord Bot
    protocol.set_logger(dbot.logger)
    # Periodic (Timer) Functions
    wait_on = []
    wait_on.append(on_con_lost)
    for f in dbot.periodic + protocol.periodic:
        task = loop.create_task(f())
        loop.call_later(2 ** 128, task.cancel)
        wait_on.append(task)
    protocol.login(protocol.username, protocol.password)  # log into PRISM
    wait_on.append(dbot.start(config["DISCORD"]["TOKEN"]))
    try:
        await asyncio.wait(wait_on, return_when=asyncio.FIRST_EXCEPTION)
    except prismbot.PrismClientProtocolConnectionLost:
        dbot.logger.log("PRISMBot lost connection.")
        transport.close()
        await dbot.close()
        return True
    except KeyboardInterrupt:
        dbot.logger.log("PRISMBot caught KeyboardInterrupt.")
        return False
    except SystemExit:
        dbot.logger.log("PRISMBot caught SystemExit.")
        return False

if __name__ == "__main__":
    try:
        ret = asyncio.run(main())
        if ret is None:
            exit(1)
        exit(int(ret))
    except:
        raise
