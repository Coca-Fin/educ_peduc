from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads

class BotHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])

        body = self.rfile.read(content_length)

        update = loads(body)

        print(update)

        self.send_response(200)
        self.end_headers()


server = HTTPServer(
    ("0.0.0.0", 8080),
    BotHandler
)
