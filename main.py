from http.server import HTTPServer

from server import Server

if __name__ == '__main__':
    server = HTTPServer(('', 8888), Server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
