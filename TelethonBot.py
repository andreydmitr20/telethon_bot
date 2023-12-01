import asyncio

# from email import message
import os
import time
import json
from telethon import TelegramClient, events
import multiprocessing as mp

from config import config
from log import log, current_utc_date_int

SECONDS_TO_ANSWER_QUIZ = 10
QUIZ_TEXT = "Welcome to the group!\n Answer during {SECONDS_TO_ANSWER_QUIZ} seconds, how much 2+2= ?"
QUIZ_ANSWER = "4".lower()


class TelethonBot:
    """TelethonBot"""

    def __init__(self, api_id: str, api_hash: str, bot_token: str):
        self.__log_pid = f"{self.__class__.__name__}-{os.getpid()}:"
        self.__api_id = api_id
        self.__bot_token = bot_token
        self.__api_hash = api_hash
        self.__bot_username = ""
        self.__client = None
        self.__user_joined_or_added_dict = {}

    def get_log_pid(self) -> str:
        """get_log_pid"""
        return self.__log_pid

    def get_bot_username(self) -> str:
        """get_bot_username"""
        return self.__bot_username

    ###### main
    async def main_loop(self):
        """main_loop"""

        await self.get_me()

        while True:
            # delete who did not pass the quiz
            utc_now = current_utc_date_int()
            for user_id, item in self.__user_joined_or_added_dict.items():
                if item["end_utc_time"] >= utc_now:
                    await self.quiz_clear(user_id, kick_user=True)

            await asyncio.sleep(1)

    async def quiz_clear(self, user_id: int, kick_user: bool = False):
        """quiz_clear"""
        item = self.__user_joined_or_added_dict.get(user_id, None)
        if item:
            group_id = item["group_id"]

            try:
                if kick_user:
                    try:
                        await self.kick_user_from_group(group_id, user_id)

                    except Exception as exception:
                        log.error(
                            "%s %s exception %s",
                            self.__log_pid,
                            "quiz_clear:",
                            exception,
                        )

                await self.delete_message(group_id, item["message_id"])
                await self.delete_message(group_id, item["replay_message_id"])

            except Exception as exception:
                log.error(
                    "%s %s exception %s", self.__log_pid, "quiz_clear:", exception
                )
            finally:
                del self.__user_joined_or_added_dict[user_id]

    async def process_new_message(self, event):
        """process_new_message"""
        log.info("%s %s", self.__log_pid, event)
        
        
        user_id = event.message.from_id.user_id
        
        # check if quiz answer
        item = self.__user_joined_or_added_dict.get(user_id, None)
        if item:
            try:
                # check quiz item
                kick_user= item["quiz_answer"] != event.message.message.strip().lower():
                # quiz has done
                await self.quiz_clear(user_id,kick_user=kick_user)
            
            except Exception as exception:
                log.error(
                    "%s %s exception %s",
                    self.__log_pid,
                    "process_new_message:",
                    exception,
                )
            finally:
                event.message.delete()

    async def process_chat_action(self, event):
        """process_chat_action"""
        pass

    async def process_user_joined_or_added(self, event):
        """process_user_joined_or_added"""
        log.info("%s %s", self.__log_pid, event)
        if event.action_message:
            user_id = event.action_message.from_id.user_id
            group_id = event.action_message.peer_id.channel_id
            message_id = event.action_message.id
            #
            reply_msg = await event.reply(
                QUIZ_TEXT.replace(
                    "{SECONDS_TO_ANSWER_QUIZ}", str(SECONDS_TO_ANSWER_QUIZ)
                )
            )
            self.__user_joined_or_added_dict[user_id] = {
                "end_utc_time": current_utc_date_int() + SECONDS_TO_ANSWER_QUIZ,
                "replay_message_id": reply_msg.id,
                "group_id": group_id,
                "message_id": message_id,
                "quiz_answer": QUIZ_ANSWER,
            }

    async def process_user_left_or_kicked(self, event):
        """process_user_left_or_kicked"""
        pass

    async def kick_user_from_group(self, group_id: int, user_id: int):
        """kick_user_from_group"""
        msg = await self.__client.kick_participant(group_id, user_id)
        await msg.delete()

    async def delete_message(self, group_id: int, message_id: int):
        """delete_message"""
        await self.__client.delete_messages(group_id, message_id)

    # exception: The API access for bot users is restricted.
    # The method you tried to invoke cannot be executed as a bot (caused by SearchRequest)
    async def delete_user_messages(self, group_id: int, user_id: int):
        """delete_user_messages"""
        async for message in self.__client.iter_messages(group_id, from_user=user_id):
            await self.__client.delete_messages(group_id, message.id)

    async def get_me(self):
        """get_me"""
        me = await self.__client.get_me()
        self.__bot_username = me.username

    ###### START
    def start(self):
        """start"""
        self.__client = TelegramClient(
            session=self.__class__.__name__,
            api_hash=self.__api_hash,
            api_id=int(self.__api_id),
        ).start(bot_token=self.__bot_token)

        with self.__client as client:

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

            client.loop.run_until_complete(self.main_loop())


#############
if __name__ == "__main__":
    bot = TelethonBot(
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
    )
    try:
        log.info("%s is starting...", bot.get_log_pid())
        bot.start()
        log.info("%s disconnected: %s", bot.get_log_pid(), bot.get_bot_username())

    except Exception as exception:
        log.error("%s exception: %s", bot.get_log_pid(), exception)
