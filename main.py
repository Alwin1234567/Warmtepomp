from http.server import HTTPServer
from server import Server, WebSocketServer
from logger import logger
from threading import Thread

if __name__ == '__main__':
    # Start the HTTP server
    httpServer = HTTPServer(('', 8888), Server)
    server = Server()


    # Start the WebSocket server in a separate thread
    websocket_server = WebSocketServer()
    websocket_thread = Thread(target=websocket_server.start)
    websocket_thread.start()

    try:
        logger.info("Server started")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logger.info("Server stopped")
