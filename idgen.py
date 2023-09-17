import http.server
import urllib.parse
import json
import time
import threading
import logging


class MySnowflake:
    def __init__(self):
        self.sequence = 0
        self.sequence_bits = 16
        self.usingTimestamp = int(time.time())
        self.namespace = 63
        self.server_id = self.alloc_server_id()
        self.lock = threading.Lock()

        self.start_refresh_thread()

    def alloc_server_id(self):
        # TODO: 添加获取server_id的逻辑
        return 63

    def start_refresh_thread(self):
        refresh_thread = threading.Thread(target=self.refresh_time)
        refresh_thread.daemon = True
        refresh_thread.start()

    def refresh_time(self):
        while True:
            current_timestamp = int(time.time())
            with self.lock:
                if current_timestamp > self.usingTimestamp:
                    self.usingTimestamp = current_timestamp
                    self.sequence = 0
            # TODO: 上报server_id+usingTimestamp逻辑，此处省略
            time.sleep(1)

    def get_single_id(self):
        with self.lock:
            remainSize = (1 << self.sequence_bits) - self.sequence
            if remainSize == 0:
                self.sequence = 0
                self.usingTimestamp += 1
            id = self.build_id(self.usingTimestamp, self.sequence, self.namespace, self.server_id)
            self.sequence += 1

        return id

    def get_batch_id(self, size):
        with self.lock:
            totalSize = size
            remainSize = (1 << self.sequence_bits) - self.sequence
            idCountUsedUp = False

            if size > remainSize:
                idCountUsedUp = True
                totalSize = remainSize

            start_id = self.build_id(self.usingTimestamp, self.sequence, self.namespace, self.server_id)

            if totalSize > 1:
                next_id = self.build_id(self.usingTimestamp, self.sequence + 1, self.namespace, self.server_id)
                step = next_id - start_id
            self.sequence += totalSize

            if idCountUsedUp:
                self.sequence = 0
                self.usingTimestamp += 1

        return start_id, step, totalSize

    def build_id(self, using_timestamp, sequence, namespace, server_id):
        id = (using_timestamp << 31) | (sequence << 15) | (namespace << 9) | server_id
        return id


snowflake = MySnowflake()


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = parsed_url.query

        if path == "/emit":
            self.handle_emit()
        elif path == "/batch_emit" and query.startswith("size="):
            self.handle_batch_emit(query)
        else:
            self.send_response(404)

    def handle_emit(self):
        try:
            id = snowflake.get_single_id()
            response = {"id": id}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logging.error("Error handling emit request: %s", str(e))
            self.send_response(500)

    def handle_batch_emit(self, query):
        try:
            params = urllib.parse.parse_qs(query)
            size = int(params.get("size", [0])[0])

            if size > 0:
                start_id, step, size = snowflake.get_batch_id(size)
                response = {
                    "start_id": start_id,
                    "step": step,
                    "size": size
                }
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
        except Exception as e:
            logging.error("Error handling batch_emit request: %s", str(e))
            self.send_response(500)


def run_server():
    server_address = ("10.0.4.11", 8080)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    logging.info("Starting server on port 8000...")
    httpd.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_server()