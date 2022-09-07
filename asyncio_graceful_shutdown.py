import asyncio
import time

from graceful_app import GracefulApp

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
            print("doing")
            await asyncio.sleep(1)
            a = []
            a[1] = 1
    except asyncio.CancelledError as e:
        print("Finalizing worker")
        await asyncio.sleep(0.2)
        print("Worker finished")

def shutdown_cb():
    print("Shutdown callback called")

async def shutdown_coro():
    await asyncio.sleep(1)
    print("Shutdown callback coro called")

if __name__ == '__main__':
    # GracefulApp(shutdown_cb,shutdown_coro).run(coroutines=[start_server, start_worker])
    GracefulApp().run(coroutines=[start_server, start_worker])