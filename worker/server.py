from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from analysis import measure


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/measure":
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        if not 0 < size <= 4_194_304:
            self.send_error(413)
            return
        try:
            result = measure(self.rfile.read(size))
        except ValueError:
            self.send_error(422)
            return
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8091), Handler).serve_forever()
