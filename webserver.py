import threading
import time
from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer
from abc import ABC, abstractmethod
import json
import asyncio
import urllib.parse

# Implementing Decorators
def log_request(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"\nFunction {func.__name__} called")
        print(f"Request from: {self.client_address}")
        print(f"Request path: {self.path}")
        result = func(self, *args, **kwargs)
        print(f"Function {func.__name__} executed\n")
        return result
    return wrapper

def authorize_request(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("Authorizing request...")
        authorized = True  
        if authorized:
            print("Request authorized")
            return func(self, *args, **kwargs)
        else:
            self.send_response(403)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "403 Forbidden", "message": "You are not authorized to access this page."}).encode())
            print("Unauthorized request")
            return 
    return wrapper

# Implementing BaseRequestHandler and Derived Classes
class BaseRequestHandler(ABC):
    @abstractmethod
    def handle_request(self, handler):
        pass

class GetRequestHandler(BaseRequestHandler):
    def handle_request(self, handler):
        client_info = {
            "client_ip": handler.client_address[0],
            "client_port": handler.client_address[1],
            "user_agent": handler.headers.get("User-Agent"),
            "content_type": handler.headers.get("Content-Type")
        }
        print(f"Handling GET request with client info: {client_info}")

        response_data = {
            "status": "success",
            "method": "GET",
            "path": handler.path,
            "message": "GET request response",
            "client_info": client_info
        }

        response_json = json.dumps(response_data, indent=4)
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()

        try:
            start_time = time.time()
            for part in streaming_response_generator(response_json):
                handler.wfile.write(part.encode())
            end_time = time.time()
            print(f"Streaming response time: {end_time - start_time:.4f} seconds")
        except (ConnectionResetError, BrokenPipeError):
            print("Connection lost while sending response")

class PostRequestHandler(BaseRequestHandler):
    def handle_request(self, handler):
        client_info = {
            "client_ip": handler.client_address[0],
            "client_port": handler.client_address[1],
            "user_agent": handler.headers.get("User-Agent"),
            "content_type": handler.headers.get("Content-Type")
        }
        print(f"Handling POST request with client info: {client_info}")

        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        new_task = post_data.get('task', [''])[0]
        
        print(f"Received data: {post_data}")

        response_data = {
            "status": "success",
            "method": "POST",
            "path": handler.path,
            "message": f"POST request data: {post_data}",
            "client_info": client_info
        }

        response_json = json.dumps(response_data, indent=4)
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()

        try:
            start_time = time.time()
            for part in streaming_response_generator(response_json):
                handler.wfile.write(part.encode())
            end_time = time.time()
            print(f"Streaming response time: {end_time - start_time:.4f} seconds")
        except (ConnectionResetError, BrokenPipeError):
            print("Connection lost while sending response")

class ShutdownRequestHandler(BaseRequestHandler):
    def handle_request(self, handler):
        print("Handling server shutdown request")
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()
        handler.wfile.write(json.dumps({"message": "Server is shutting down..."}).encode())
        threading.Thread(target=handler.server.shutdown).start()

# Implementing Request Handler Class
class RequestHandler(BaseHTTPRequestHandler):
    @log_request
    @authorize_request
    def do_GET(self):
        print("Function do_GET called")
        handler = GetRequestHandler()
        handler.handle_request(self)
        print("Function do_GET executed")

    @log_request
    @authorize_request
    def do_POST(self):
        if self.path == '/shutdown':
            handler = ShutdownRequestHandler()
        else:
            handler = PostRequestHandler()
        print("Function do_POST called")
        handler.handle_request(self)
        print("Function do_POST executed")

# Implementing Generators
def streaming_response_generator(message):
    chunk_size = 50  # Increase the chunk size for fewer print statements
    total_chunks = (len(message) + chunk_size - 1) // chunk_size
    print(f"Total message length: {len(message)} characters")
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i + chunk_size]
        print(f"Streaming chunk: {chunk}")
        yield chunk
    print("Completed streaming all chunks.")

# Implementing Iterator
class RequestIterator:
    def __init__(self, requests):
        self._requests = requests
        self._index = 0
        print("Initialized RequestIterator with requests:", requests)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._requests):
            result = self._requests[self._index]
            print(f"RequestIterator returning request at index {self._index}: {result}")
            self._index += 1
            return result
        else:
            print("RequestIterator reached end of requests")
            raise StopIteration

    def __len__(self):
        return len(self._requests)

# Implementing Async Iterator
class AsyncRequestIterator:
    def __init__(self, request_iterator):
        self._request_iterator = request_iterator
        self._requests = list(request_iterator)
        self._index = 0
        print("Initialized AsyncRequestIterator with requests:", self._requests)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index < len(self._requests):
            result = self._requests[self._index]
            print(f"AsyncRequestIterator returning request at index {self._index}: {result}")
            self._index += 1
            await asyncio.sleep(0)  # Simulate async processing time
            return result
        else:
            print("AsyncRequestIterator reached end of requests")
            raise StopAsyncIteration

async def async_request_handler(request_iterator):
    print("async_request_handler called")
    async for request in AsyncRequestIterator(request_iterator):
        print(f"Processing request asynchronously: {request}")
        await asyncio.sleep(1)
    print("async_request_handler executed")

# Implementing Singleton Pattern
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class WebServer(metaclass=SingletonMeta):
    def __init__(self, server_address, handler_class):
        self.server = HTTPServer(server_address, handler_class)

# Implementing Context Manager
class ServerContextManager:
    def __init__(self, server_address, handler_class):
        self.server_instance = WebServer(server_address, handler_class)

    def __enter__(self):
        start_time = time.time()
        print("Initializing ServerContextManager")
        end_time = time.time()
        print(f"ServerContextManager initialized in {end_time - start_time:.4f} seconds")
        print(f"Starting server on {self.server_instance.server.server_address}...")
        return self.server_instance.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Shutting down server")
        self.server_instance.server.shutdown()
        self.server_instance.server.server_close()

# Running the Web Server
def run():
    server_address = ('0.0.0.0', 9000)
    handler_class = RequestHandler
    print("Setting up server: Initializing HTTP server and handler class")

    with ServerContextManager(server_address, handler_class) as httpd:
        print("*************** Welcome to Maha's Server ***************")
        print(f"---------\nServer running at http://{server_address[0]}:{server_address[1]}\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run()