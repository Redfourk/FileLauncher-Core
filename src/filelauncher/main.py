import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from core.airlock import AirlockPipeline
from core.commands import CommandProcessor

backend_version = "0.0.1"

"""Initialize server framework components."""
airlock = AirlockPipeline()
processor = CommandProcessor()

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


class ConsoleLoggingHandler(logging.Handler):
    """Custom log handler that color-codes logs based on their severity
       and clears the input line so it doesn't mess up the prompt."""

    def emit(self, record):
        log_entry = self.format(record)
        color = RESET
        if record.levelno >= logging.ERROR:
            color = RED
        elif record.levelno >= logging.WARNING:
            color = YELLOW
        elif record.levelno >= logging.INFO:
            color = CYAN

        # Print with color applied, then reset and restore prompt
        print(f"\r\033[K{color}{log_entry}{RESET}\nMODERATOR >> ", end="", flush=True)


class FileLauncherAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle incoming POST requests (File Uploads or Commands)"""
        if self.path == "/upload":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_response(400, {"error": "No content provided"})
                return

            filename = self.headers.get('X-File-Name', 'unknown_file.bin')

            logging.info(f"Receiving {content_length} bytes for {filename}...")
            file_data = self.rfile.read(content_length)

            result = airlock.process_incoming_file(filename, file_data)

            status_code = 200 if result["status"] == "success" else 403
            self._send_response(status_code, result)

        elif self.path == "/command":
            content_length = int(self.headers.get('Content-Length', 0))
            command_data = self.rfile.read(content_length).decode('utf-8')
            response_msg = processor.execute(command_data)
            self._send_response(200, {"result": response_msg})
        else:
            self._send_response(404, {"error": "Route not found"})

    def _send_response(self, status_code, data_dict):
        """Helper to send JSON responses back to the client"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data_dict).encode('utf-8'))


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = ConsoleLoggingHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root_logger.handlers = [handler]


def moderator_console():
    """Runs a local terminal loop with color-coded feedback for results."""
    while True:
        try:
            cmd = input("MODERATOR >> ")
            if cmd.strip():
                result = processor.execute(cmd)
                color = RED if "Error" in result else GREEN
                print(f"Result: {color}{result}{RESET}\nMODERATOR >> ", end="", flush=True)
        except EOFError:
            break


def start_server():
    host = '0.0.0.0'
    port = 8080
    server = HTTPServer((host, port), FileLauncherAPI)
    logging.info(f"FileLauncher-Core Backend listening on http://{host}:{port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Shutting down server...{RESET}")
        server.server_close()


if __name__ == "__main__":
    setup_logging()

    console_thread = threading.Thread(target=moderator_console, daemon=True)
    console_thread.start()

    start_server()