import asyncio
from telethon import TelegramClient, events
from config import config


async def run():
    print("start")

    client = await TelegramClient(
        session="test",
        api_hash=config.api_hash,
        api_id=int(config.api_id),
    ).start(bot_token=config.bot_token)

    async with client:
        try:
            me = await client.get_me()
            print(f"{me}")
        except Exception as exception:
            print("Failed to get me")
            return

        @client.on(events.NewMessage)
        async def my_event_handler(event):
            """my_event_handler"""
            print(f"{event}")

        await client.run_until_disconnected()


################
if __name__ == "__main__":
    asyncio.run(run())
