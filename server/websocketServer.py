import asyncio
import websockets
import subprocess
import os
import glob

class WebSocketServer:
    """
    A WebSocket server that streams the most recent log file to connected clients.
    """

    def __init__(self, host='localhost', port=5678):
        """
        Initializes the WebSocket server.

        Args:
            host (str): The host to listen on.
            port (int): The port to listen on.
        """
        self.host = host
        self.port = port
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

    async def send_console_output(self, websocket, path):
        """
        Sends the console output from the most recent log file to the WebSocket client.

        :param websocket: The WebSocket connection.
        :param path: The request path.
        """
        # Find the most recent log file
        log_files = sorted(glob.glob(os.path.join(self.log_dir, 'debug.log*')), key=os.path.getmtime)
        if log_files:
            latest_log_file = log_files[-1]
        else:
            latest_log_file = os.path.join(self.log_dir, 'debug.log')
        
        process = subprocess.Popen(['tail', '-f', latest_log_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if not line:
                break
            await websocket.send(line.decode('utf-8'))

    def start(self):
        """
        Starts the WebSocket server.
        """
        start_server = websockets.serve(self.send_console_output, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    server = WebSocketServer()
    server.start()
