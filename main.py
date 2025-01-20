import os
import signal
import subprocess
from http.server import HTTPServer
from server import Server

def handle_restart_signal(signum, frame):
    """Handle the restart signal by stopping the server and running setupAndRun.sh"""
    print("Received restart signal. Restarting the server...")
    server.server_close()
    subprocess.run(["/bin/bash", "setupAndRun.sh"])

if __name__ == '__main__':
    server = HTTPServer(('', 8888), Server)
    signal.signal(signal.SIGUSR1, handle_restart_signal)
    try:
        print("Starting server on port 8888")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server closed")
