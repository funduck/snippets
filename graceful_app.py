import asyncio
import logging
import signal
import sys
from typing import Callable, List


class GracefulApp:
    """
    Allows to run multiple coroutines as main 'processes' of the app and gracefully exit
    """
    def __init__(self, shutdown_cb: Callable = None, shutdown_coro: Callable = None, logger = None) -> None:
        """
        shutdown_cb - sync function will be called after all asyncio tasks finish
        shutdown_coro - async function will be awaited after shutdown_cb if provided any

        Logger is used for printing traceback of Exception and for ordinary logging, provide methods:
        * exception(e: Exception)
        * debug(msg: str)
        * info(msg: str)
        * fatal(msg: str)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.__shutdown_cb = shutdown_cb
        self.__shutdown_coro = shutdown_coro

    def _shutdown(self, signum, *_):
        self.logger.info(f"Received exit signal {signal.Signals(signum).name}={signum} {signal.strsignal(signum)} ...")
        tasks = [t for t in asyncio.all_tasks()]
        for task in tasks:
            task.cancel()

    def handle_fatal_exception(self, task: asyncio.Task, exit_code=1) -> None:
        """
        Attaches a handler to task, that will terminate the program
        """
        try:
            task.result()
        except asyncio.CancelledError:
            pass  # Task cancellation should be processed in the task
        except Exception as e:  # pylint: disable=broad-except
            self.logger.fatal(f'Exception raised by task = {task}')
            self.logger.exception(e)
            sys.exit(exit_code)

    def run(self, coroutines: List[Callable]):
        """
        Runs coroutines forever
        If any coroutine raises Exception, app terminates gracefully
        If the process receives termination signal, app will cancel all asyncio tasks and exit
        """
        for s in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(s, self._shutdown)

        async def runner():
            tasks = []
            try:
                tasks = [asyncio.create_task(coro()) for coro in coroutines]
                for task in tasks:
                    task.add_done_callback(self.handle_fatal_exception)
                await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            except asyncio.CancelledError:
                await asyncio.wait(tasks)
                if self.__shutdown_cb:
                    self.logger.debug("Running shutdown callback")
                    self.__shutdown_cb()
                if self.__shutdown_coro:
                    self.logger.debug("Running shutdown callback coroutine")
                    await self.__shutdown_coro()

        asyncio.run(runner())
