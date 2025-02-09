from .serverInstance import HttpServerInstance
from http.server import BaseHTTPRequestHandler, HTTPServer
from handler import Browser
import socketserver
from typing import Tuple
from logger import logger
from config import WarmtepompSettings as WS
from config import Config
import os
from time import sleep
import sys
from logic import AlwinHome
import json

class HttpHandler(BaseHTTPRequestHandler):
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
        self.alwinHome = AlwinHome()


    def do_POST(self):
        """Handles the POST requests"""
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length).decode('utf8')
        
        try:
            json_data: dict = json.loads(data)
            command = json_data["command"]
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        if command == "wp auto":
            try:
                self.browser.get_set_warmtepompen(WS.AUTO)
            except Exception as e:
                logger.error(f"Error while trying to set warmtepompen to auto: {e}")
                try:
                    self.browser.quit_browser()
                except Exception as e:
                    logger.error(f"Error while trying to quit browser: {e}")
        elif command == "wp off":
            try:
                self.browser.get_set_warmtepompen(WS.OFF)
            except Exception as e:
                logger.error(f"Error while trying to set warmtepompen to off: {e}")
                try:
                    self.browser.quit_browser()
                except Exception as e:
                    logger.error(f"Error while trying to quit browser: {e}")
        
        elif command == "test": 
            logger.info("Test")
        
        elif command == "restart":
            logger.info("Received restart command")
            self.send_response(200)
            self.end_headers()            
            self.wfile.write(b"Restarting server")
            self.wfile.flush()
            if self.browser and self.browser.browser:
                sleep(2)
                self.browser.quit_browser()
            if HttpServerInstance.serverInstance:
                sleep(1)
                HttpServerInstance.serverInstance.server_close()
                sys.exit(0)

        elif command == "ping":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Pong")
            logger.info("Received ping")
        
        elif command == 'Alwin home':
            missingWeekday = False
            if "weekday" not in json_data:
                missingWeekday = True
            weekday = json_data.get("weekday", "sunday")
            if weekday.lower().strip() not in Config.WEEKDAYS:
                weekday = "sunday"
                missingWeekday = True
            self.alwinHome.setHome(dayStr=weekday)
            self.send_response(200)
            self.end_headers()
            if missingWeekday:
                self.wfile.write(b"missing or invalid weekday, setting Alwin home until sunday")
            else:
                self.wfile.write(f"Setting Alwin home until {weekday}".encode('utf-8'))
        
        elif command == 'Alwin away':
            self.alwinHome.setAway()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Setting Alwin away")


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
    server = HTTPServer(('', 8888), HttpHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
