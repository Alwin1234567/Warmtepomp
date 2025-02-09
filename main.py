from http.server import HTTPServer
from server import HttpHandler, HttpServerInstance
from logger import logger
import sys

# async def start_websocket_server(websocket_server):
#     await websocket_server.start()

if __name__ == '__main__':
    # Start the HTTP server
    server = HTTPServer(('', 8888), HttpHandler)

    # # Start the WebSocket server in a separate thread
    # websocket_server = WebSocketServer()
    # websocket_thread = Thread(target=lambda: asyncio.run(start_websocket_server(websocket_server)))
    # websocket_thread.start()

    HttpServerInstance.serverInstance = server

    try:
        logger.info("Server started")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError:
        pass
    finally:
        server.server_close()
        logger.info("Server stopped")
