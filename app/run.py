import asyncio

from app.api.create_app import run_server
from app.bot.create_bot import run_bot
from database.database import delete_tables, create_tables


async def run():
    # await delete_tables()
    await create_tables()
    tasks = [
        asyncio.ensure_future(run_bot()),
        asyncio.ensure_future(run_server()),

    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(run())
