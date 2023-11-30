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
        async def message_handler(event):
            """message_handler"""
            print(f"{event}")

        @client.on(events.ChatAction)
        async def chat_handler(event):
            """chat_handler"""
            if (
                event.user_joined
                or event.user_added
                or event.user_left
                or event.user_kicked
            ):
                # await event.reply('Welcome to the group!')
                print(f"{event}")

        await client.run_until_disconnected()


################
if __name__ == "__main__":
    asyncio.run(run())
