from http.server import BaseHTTPRequestHandler, HTTPServer
from handler import Browser
import socketserver
from typing import Tuple
from logger import logger
from config import WarmtepompSettings as WS
import traceback
import os
from time import sleep

class ServerRestartException(Exception):
    pass

class Server(BaseHTTPRequestHandler):
    """class to handle the http requests"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        """Initializes the server"""
        try:
            self.browser = Browser()
        except Exception as e:
            logger.error(f"Error while initializing browser: {e}")
        current_dir = os.path.dirname(__file__)
        self.htmlIndexFile = os.path.join(current_dir, 'index.html')
        super().__init__(request, client_address, server)

    
    def do_POST(self):
        """Handles the POST requests"""
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length).decode('utf8')
        
        if data == "wp auto":
            try:
                self.browser.get_set_warmtepompen(WS.AUTO)
            except Exception as e:
                logger.error(f"Error while trying to set warmtepompen to auto: {e}\n{traceback.format_exc()}")
                try:
                    self.browser.quit_browser()
                except Exception as e:
                    logger.error(f"Error while trying to quit browser: {e}")
        elif data == "wp off":
            try:
                self.browser.get_set_warmtepompen(WS.OFF)
            except Exception as e:
                logger.error(f"Error while trying to set warmtepompen to off: {e}")
                try:
                    self.browser.quit_browser()
                except Exception as e:
                    logger.error(f"Error while trying to quit browser: {e}")
        elif data == "test": 
            logger.info("Test")
        elif data == "restart":
            logger.info("Received restart command")
            self.send_response(200)
            self.end_headers()            
            self.wfile.write(b"Restarting server")
            logger.info("Restarting server...")
            # subprocess.run(["/bin/bash", os.path.join(self.current_dir, 'setupAndRun.sh')])
            if self.browser and self.browser.browser:
                sleep(1)
                self.browser.quit_browser()
            raise ServerRestartException("Restarting server")
        elif data == "ping":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Pong")
            logger.info("Received ping")
            
        else:
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Invalid command")
            logger.warning(f"Received invalid command: {data}")
            return
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handles the GET requests"""
        try:
            with open(self.htmlIndexFile[1:], 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

        
if __name__ == '__main__':
    server = HTTPServer(('', 8888), Server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
