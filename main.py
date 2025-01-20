import signal
import subprocess
from http.server import HTTPServer
from server import Server, WebSocketServer
from logger import logger
from threading import Thread

def handle_restart_signal(signum, frame):
    """Handle the restart signal by stopping the server and running setupAndRun.sh"""
    print("Received restart signal. Restarting the server...")
    server.server_close()
    subprocess.run(["/bin/bash", "setupAndRun.sh"])

if __name__ == '__main__':
    # Start the HTTP server
    server = HTTPServer(('', 8888), Server)
    signal.signal(signal.SIGUSR1, handle_restart_signal)

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
