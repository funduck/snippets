import asyncio
import signal
import sys
import time

async def start_server():
    async def handle_healthcheck(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        message = f'HTTP/1.1 503 SERVICE UNAVAILABLE\r\n\r\nNOT HEALTHY {time.time()}'
        # message = f'HTTP/1.1 200 OK\r\n\r\HEALTHY {time.time()}'
        writer.write(message.encode('utf8'))
        await writer.drain()
        if writer.can_write_eof():
            writer.write_eof()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(
        handle_healthcheck, "0.0.0.0", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        print("Closing server")
        server.close()
        await server.wait_closed()
        print("Server closed")

async def start_worker():
    try:
        while True:
            # print("doing")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Finalizing work")
        await asyncio.sleep(0.2)
        print("Work finished")

# def run_with_event():
#     """
#     With event to finish special coroutine
#     main finished will be printed
#     """
#     event_terminate = asyncio.Event()

#     async def start_termination_listener():
#         nonlocal event_terminate
#         while not event_terminate.is_set():
#             await asyncio.sleep(0.1)

#     signal.signal(signal.SIGINT, lambda *_: event_terminate.set())

#     async def main():
#         await asyncio.wait([asyncio.create_task(coro) for coro in [
#             start_server(),
#             start_worker(),
#             start_termination_listener()
#         ]], return_when=asyncio.FIRST_COMPLETED)
#         print("main finished")

#     return main

# def run_with_exit():
#     """
#     With sys.exit
#     main finished not printed
#     """
#     signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

#     async def main():
#         await asyncio.wait([asyncio.create_task(coro) for coro in [start_server(), start_worker()]])
#         print("main finished")

#     return main

def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception:  # pylint: disable=broad-except
        print(f'Exception raised by task = {task}')
        sys.exit(1)

def run_with_except():
    """
    With try except CancelledError
    main finished not printed
    """
    async def main():
        tasks = []
        try:
            tasks = [asyncio.create_task(coro) for coro in [start_server(), start_worker()]]
            for task in tasks:
                task.add_done_callback(_handle_task_result)
            await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        except asyncio.CancelledError:
            await asyncio.wait(tasks)
            print("Finishing main")
            await asyncio.sleep(0.5)
            print("Main finished")

    return main

def shutdown(signum, *_):
    print(f"Received exit signal {signal.Signals(signum).name}={signum} {signal.strsignal(signum)} ...")
    tasks = [t for t in asyncio.all_tasks()]
    for task in tasks:
        task.cancel()

for s in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(s, shutdown)
asyncio.run(run_with_except()())
