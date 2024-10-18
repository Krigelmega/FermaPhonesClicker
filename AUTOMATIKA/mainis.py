import asyncio
from contextlib import suppress
from AUTOMATIKA.bot.utils.launcher import process



async def main():
    await process()



def mainis():
    with suppress(KeyboardInterrupt):
        asyncio.run(main())



