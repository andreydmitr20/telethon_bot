import asyncio
import os
import time
import multiprocessing as mp


class WorkerWithPipe:
    """WorkerWithPipe"""

    def __init__(self, worker_async_function) -> None:
        self.__worker_parent_pipe = None
        self.__worker_child_pipe = None
        self.__process = None
        self.__worker_async_function = worker_async_function

    def get_parent_pipe(self):
        """get_parent_pipe"""
        return self.__worker_parent_pipe

    def get_child_pipe(self):
        """get_child_pipe"""
        return self.__worker_child_pipe

    async def get_message_from_pipe(self, pipe):
        """get_message_from_pipe"""
        if pipe and pipe.poll():
            income_message = pipe.recv()
            # income_message = await pipe.recv()
            return income_message
        return None

    async def get_message_from_child_pipe(self):
        return await self.get_message_from_pipe(self.__worker_child_pipe)

    async def get_message_from_parent_pipe(self):
        return await self.get_message_from_pipe(self.__worker_parent_pipe)

    async def send_message_to_pipe(self, message_to_send, pipe):
        """send_message_to_pipe"""
        print(pipe)
        print()
        print(message_to_send)
        if pipe:
            # await pipe.send(message_to_send)
            pipe.send(message_to_send)

    async def send_message_to_child_pipe(self, message_to_send):
        await self.send_message_to_pipe(message_to_send, self.__worker_child_pipe)

    async def send_message_to_parent_pipe(self, message_to_send):
        await self.send_message_to_pipe(message_to_send, self.__worker_parent_pipe)

    def worker_process(self, async_function, child_pipe):
        """worker_process"""
        asyncio.run(async_function(child_pipe))

    def __enter__(self):
        """run_worker_process"""
        self.__worker_parent_pipe, self.__worker_child_pipe = mp.Pipe()

        self.__process = None
        self.__process = mp.Process(
            target=self.worker_process,
            args=(
                self.__worker_async_function,
                self.__worker_child_pipe,
            ),
        )
        self.__process.daemon = True  # Set the process as a daemon
        self.__process.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.__process and self.__process.is_alive():
                self.__process.terminate()
                self.__process = None
        except:
            pass
        try:
            if self.__worker_child_pipe:
                self.__worker_child_pipe.close()
                self.__worker_child_pipe = None
        except:
            pass
        try:
            if self.__worker_parent_pipe:
                self.__worker_parent_pipe.close()
                self.__worker_parent_pipe = None
        except:
            pass


########
if __name__ == "__main__":

    async def test_worker(child_pipe):
        """test_worker"""

        async def get_message_from_pipe():
            """get_message_from_pipe"""
            if child_pipe and child_pipe.poll():
                income_message = child_pipe.recv()
                return income_message
            return None

        while True:
            time.sleep(1)
            message = await get_message_from_pipe()
            if message:
                print(message)
                if message == str(5):
                    break

    async def test():
        """test"""
        with WorkerWithPipe(test_worker) as worker:
            counter = 0
            while True:
                time.sleep(2)
                print(f">>{counter}")
                worker.get_parent_pipe().send(str(counter))
                # await worker.send_message_to_parent_pipe(str(counter))
                counter += 1

    asyncio.run(test())
