import asyncio
from telethon import TelegramClient, events
from config import config


async def run():
    print("start")

    client = TelegramClient(
        session="test",
        api_hash=config.api_hash,
        api_id=int(config.api_id),
    )

    @client.on(events.NewMessage)
    async def my_event_handler(event):
        """my_event_handler"""
        print(f"{event}")

    async with client:
        try:
            await client.sign_in(bot_token=config.bot_token, phone=config.phone)
        except Exception as exc:
            print("Failed to sign in")
            return

        try:
            me = await client.get_me()
            print(f"{me}")
        except Exception as exception:
            print("Failed to get me")
            return

        await client.run_until_disconnected()


################
if __name__ == "__main__":
    asyncio.run(run())
