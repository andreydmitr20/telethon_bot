from telethon import TelegramClient, events
from config import config

client = TelegramClient("session_read", config.api_id, config.api_hash)


@client.on(events.NewMessage)
async def my_event_handler(event):
    print("{}".format(event))


client.start()
client.run_until_disconnected()
