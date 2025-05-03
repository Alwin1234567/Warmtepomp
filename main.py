from http.server import HTTPServer
from server import HttpHandler, HttpServerInstance
from logger import logger
from logic import Scheduler
from asyncio import create_task
import asyncio

# async def start_websocket_server(websocket_server):
#     await websocket_server.start()

async def run(scheduler):
    scheduler_task = None
    try:
        scheduler_task = create_task(scheduler.run())
    except Exception as e:
        logger.error(f"Error while running scheduler: {e}")

    try:
        logger.info("Server started")
        await asyncio.to_thread(server.serve_forever)
    except KeyboardInterrupt:
        pass
    except OSError:
        pass
    finally:
        scheduler.stop = True
        if scheduler_task:
            scheduler_task.cancel()
        server.server_close()
        logger.info("Server stopped")


if __name__ == '__main__':
    # Start the HTTP server
    server = HTTPServer(('', 8888), HttpHandler)

    # # Start the WebSocket server in a separate thread
    # websocket_server = WebSocketServer()
    # websocket_thread = Thread(target=lambda: asyncio.run(start_websocket_server(websocket_server)))
    # websocket_thread.start()

    HttpServerInstance.serverInstance = server

    try:
        scheduler = Scheduler()
    except Exception as e:
        logger.error(f"Error while initializing scheduler: {e}")

    asyncio.run(run(scheduler))
