from http.server import BaseHTTPRequestHandler, HTTPServer
from Browser import Browser
import socketserver
from typing import Tuple

class HTTPRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        self.browser = Browser()
        super().__init__(request, client_address, server)
        
    
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length).decode('utf8')
        
        if data == "wp auto": self.browser.get_set_warmtepompen("auto")
        elif data == "wp off": self.browser.get_set_warmtepompen("off")
        elif data == "test": print("test")
            
        else:
            self.send_response(403)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(403)
        self.end_headers()

        
if __name__ == '__main__':
    server = HTTPServer(('', 8888), HTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()