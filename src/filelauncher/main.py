import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.airlock import AirlockPipeline

airlock = AirlockPipeline()


class FileLauncherAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle incoming POST requests (File Uploads)"""
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
        else:
            self._send_response(404, {"error": "Route not found"})

    def _send_response(self, status_code, data_dict):
        """Helper to send JSON responses back to the client"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data_dict).encode('utf-8'))


def start_server():
    host = '0.0.0.0'
    port = 8080
    server = HTTPServer((host, port), FileLauncherAPI)
    logging.info(f"FileLauncher-Core Backend listening on http://{host}:{port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    start_server()