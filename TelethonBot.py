import asyncio
import os
import time

from telethon import TelegramClient, events

from config import config
from log import log


class TelethonBot:
    """TelethonBot"""

    def __init__(self, api_id: str, api_hash: str, bot_token: str):
        self.__log_pid = f"{self.__class__.__name__}-{os.getpid()}:"
        self.__api_id = api_id
        self.__bot_token = bot_token
        self.__api_hash = api_hash
        self.__bot_username = ""
        self.__client = None
        self.__answer = None
        self.__answer_user_id = None

    def get_log_pid(self) -> str:
        """get_log_pid"""
        return self.__log_pid

    def get_bot_username(self) -> str:
        """get_bot_username"""
        return self.__bot_username

    async def start(self):
        """start"""
        self.__client = await TelegramClient(
            session=self.__class__.__name__,
            api_hash=self.__api_hash,
            api_id=int(self.__api_id),
        ).start(bot_token=self.__bot_token)
        async with self.__client as client:
            me = await client.get_me()
            self.__bot_username = me.username

            @client.on(events.NewMessage)
            async def message_handler(event):
                """message_handler"""
                await self.process_new_message(event)

            @client.on(events.ChatAction)
            async def chat_handler(event):
                """chat_handler"""
                if event.user_joined or event.user_added:
                    await self.process_user_joined_or_added(event)
                elif event.user_left or event.user_kicked:
                    await self.process_user_left_or_kicked(event)
                else:
                    await self.process_chat_action(event)

            # loop
            await client.run_until_disconnected()

    async def process_new_message(self, event):
        """process_new_message"""
        if self.__answer_user_id == event.message.from_id.user_id:
            self.__answer = event.message.message
            await self.delete_message(
                event.message.peer_id.channel_id, event.message.id
            )
            return

    async def process_chat_action(self, event):
        """process_chat_action"""
        pass

    async def process_user_joined_or_added(self, event):
        """process_user_joined_or_added"""
        log.info("%s %s", self.__log_pid, event)
        if event.action_message:
            reply_msg = None
            try:
                seconds = 10
                self.__answer = None
                self.__answer_user_id = event.action_message.from_id.user_id
                group_id = event.action_message.peer_id.channel_id
                message_id = event.action_message.id
                reply_msg = await event.reply(
                    f"Welcome to the group!\n Answer during {seconds} seconds, how much 2+2= ?"
                )
                while self.__answer is None and seconds > 0:
                    time.sleep(1)
                    seconds -= 1
                    log.info("%s %s", self.__log_pid, seconds)

                if not self.__answer:
                    user_id = self.__answer_user_id
                    try:
                        # delete message
                        # await self.delete_message(group_id, message_id)
                        # delete user
                        await self.kick_user_from_group(group_id, user_id)
                        await event.action_message.delete()
                    except Exception as exception:
                        log.error("%s exception: %s", self.__log_pid, exception)
            finally:
                self.__answer_user_id = None
                self.__answer = None
                if reply_msg:
                    await reply_msg.delete()

    async def process_user_left_or_kicked(self, event):
        """process_user_left_or_kicked"""
        pass

    async def kick_user_from_group(self, group_id: int, user_id: int):
        """kick_user_from_group"""
        msg = await self.__client.kick_participant(group_id, user_id)
        await msg.delete()

    async def delete_message(self, group_id: int, message_id: int):
        """delete_message"""
        await self.__client.delete_messages(int(group_id), int(message_id))

    # exception: The API access for bot users is restricted.
    # The method you tried to invoke cannot be executed as a bot (caused by SearchRequest)
    async def delete_user_messages(self, group_id: int, user_id: int):
        """delete_user_messages"""
        async for message in self.__client.iter_messages(
            int(group_id), from_user=int(user_id)
        ):
            await self.__client.delete_messages(int(group_id), message.id)


#############
if __name__ == "__main__":
    bot = TelethonBot(
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
    )
    try:
        log.info("%s try to start", bot.get_log_pid())
        asyncio.run(bot.start())
        log.info("%s disconnected bot: %s", bot.get_log_pid(), bot.get_bot_username())

    except Exception as exception:
        log.error("%s exception: %s", bot.get_log_pid(), exception)
