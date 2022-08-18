import asyncio
import signal
import sys

async def start_server():
    async def handle_echo(reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info("peername")

        print(f"Received {message!r} from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

        print("Close the connection")
        writer.close()

    server = await asyncio.start_server(
        handle_echo, "127.0.0.1", 8888)

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
            print("doing")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Finalizing work")
        await asyncio.sleep(0.2)
        print("Work finished")

def run_with_event():
    """
    With event to finish special coroutine
    main finished will be printed
    """
    event_terminate = asyncio.Event()

    async def start_termination_listener():
        nonlocal event_terminate
        while not event_terminate.is_set():
            await asyncio.sleep(0.1)

    signal.signal(signal.SIGINT, lambda *_: event_terminate.set())

    async def main():
        await asyncio.wait([asyncio.create_task(coro) for coro in [
            start_server(),
            start_worker(),
            start_termination_listener()
        ]], return_when=asyncio.FIRST_COMPLETED)
        print("main finished")

    return main

def run_with_exit():
    """
    With sys.exit
    main finished not printed
    """
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

    async def main():
        await asyncio.wait([asyncio.create_task(coro) for coro in [start_server(), start_worker()]])
        print("main finished")

    return main

def run_with_except():
    """
    With try except KeyboardInterrupt
    main finished not printed
    """
    async def main():
        tasks = []
        try:
            tasks = [asyncio.create_task(coro) for coro in [start_server(), start_worker()]]
            await asyncio.wait(tasks)
        except asyncio.CancelledError:
            await asyncio.wait(tasks)
            print("Finishing main")
            await asyncio.sleep(0.5)
            print("Main finished")

    return main

try:
    asyncio.run(run_with_except()())
except KeyboardInterrupt:
    print("Loop end")