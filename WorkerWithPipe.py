import asyncio
import os
import time
import multiprocessing as mp


class WorkerWithPipe:
    """WorkerWithPipe"""

    def __init__(self, worker_async_function) -> None:
        self.__worker_parent_pipe, self.__worker_child_pipe = mp.Pipe()
        self.__process = None
        self.__worker_async_function = worker_async_function

    def get_parent_pipe(self):
        """get_parent_pipe"""
        return self.__worker_parent_pipe

    def get_child_pipe(self):
        """get_child_pipe"""
        return self.__worker_child_pipe

    def get_message_from_pipe(self, pipe):
        """get_message_from_pipe"""
        if pipe and pipe.poll():
            income_message = pipe.recv()
            return income_message
        return None

    def get_message_from_child_pipe(self):
        return self.get_message_from_pipe(self.__worker_child_pipe)

    def get_message_from_parent_pipe(self):
        return self.get_message_from_pipe(self.__worker_parent_pipe)

    def send_message_to_pipe(self, message_to_send, pipe):
        """send_message_to_pipe"""
        if pipe:
            pipe.send(message_to_send)

    def send_message_to_child_pipe(self, message_to_send):
        self.send_message_to_pipe(message_to_send, self.__worker_child_pipe)

    def send_message_to_parent_pipe(self, message_to_send):
        self.send_message_to_pipe(message_to_send, self.__worker_parent_pipe)

    def worker_process(self):
        """worker_process"""
        asyncio.run(self.__worker_async_function(self))

    def __enter__(self):
        """run_worker_process"""
        self.__process = None
        self.__process = mp.Process(target=self.worker_process, args=())
        self.__process.daemon = True  # Set the process as a daemon
        self.__process.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__process and self.__process.is_alive():
            self.__process.terminate()
            self.__process = None


########
if __name__ == "__main__":

    async def test_worker(worker: WorkerWithPipe):
        """test_worker"""
        while True:
            time.sleep(1)
            message = worker.get_message_from_child_pipe()
            if message:
                print(message)

    async def test():
        """test"""
        with WorkerWithPipe(test_worker) as worker:
            counter = 0
            while True:
                time.sleep(2)
                worker.send_message_to_parent_pipe(str(counter))
                counter += 1

    asyncio.run(test())
