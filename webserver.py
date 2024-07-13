import time
from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer
from abc import ABC, abstractmethod
import json
import urllib.parse
import asyncio

# Task list to store tasks
tasklist = []

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
        authorized = True  # Simulate authorization check
        if authorized:
            print("Request authorized")
            return func(self, *args, **kwargs)
        else:
            self.send_response(403)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>403 Forbidden</h1><p>You are not authorized to access this page.</p></body></html>")
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
        if handler.path.endswith('/tasklist'):
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html')
            handler.end_headers()
            output = '''
            <html>
                <body>
                    <h1>Task List</h1>
                    <h3><a href="/tasklist/new">Add New Task</a></h3>
            '''
            for task in tasklist:
                output += f'{task} <a href="/tasklist/{task}/remove">X</a><br>'
            output += '</body></html>'
            handler.wfile.write(output.encode())
        elif handler.path.endswith('/tasklist/new'):
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html')
            handler.end_headers()
            output = '''
            <html>
                <body>
                    <h1>Add New Task</h1>
                    <form method="POST" action="/tasklist/new">
                        <input name="task" type="text" placeholder="Add new task">
                        <input type="submit" value="Add">
                    </form>
                </body>
            </html>
            '''
            handler.wfile.write(output.encode())
        else:
            client_info = {
                "client_address": handler.client_address,
                "user_agent": handler.headers.get("User-Agent"),
                "accept_language": handler.headers.get("Accept-Language"),
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
                for part in streaming_response_generator(response_json):
                    handler.wfile.write(part.encode())
            except (ConnectionResetError, BrokenPipeError):
                print("Connection lost while sending response")

class PostRequestHandler(BaseRequestHandler):
    def handle_request(self, handler):
        if handler.path.endswith('/tasklist/new'):
            content_length = int(handler.headers['Content-Length'])
            post_data = handler.rfile.read(content_length).decode('utf-8')
            post_data = urllib.parse.parse_qs(post_data)
            new_task = post_data.get('task', [''])[0]
            if new_task:
                tasklist.append(new_task)
            handler.send_response(301)
            handler.send_header('Content-type', 'text/html')
            handler.send_header('Location', '/tasklist')
            handler.end_headers()
            print(f"Current task list: {tasklist}")
            return

        client_info = {
            "client_address": handler.client_address,
            "user_agent": handler.headers.get("User-Agent"),
            "accept_language": handler.headers.get("Accept-Language"),
            "content_type": handler.headers.get("Content-Type")
        }
        print(f"Handling POST request with client info: {client_info}")

        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length)
        print(f"Received data: {post_data}")

        response_data = {
            "status": "success",
            "method": "POST",
            "path": handler.path,
            "message": f"POST request data: {post_data.decode('utf-8')}",
            "client_info": client_info
        }

        response_json = json.dumps(response_data, indent=4)
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.end_headers()

        try:
            for part in streaming_response_generator(response_json):
                handler.wfile.write(part.encode())
        except (ConnectionResetError, BrokenPipeError):
            print("Connection lost while sending response")

# Implementing Request Handler Class
class RequestHandler(BaseHTTPRequestHandler):
    @log_request
    @authorize_request
    def do_GET(self):
        print("Function handle_get called")
        handler = GetRequestHandler()
        handler.handle_request(self)
        print("Function handle_get executed")

    @log_request
    @authorize_request
    def do_POST(self):
        print("Function handle_post called")
        handler = PostRequestHandler()
        handler.handle_request(self)
        print("Function handle_post executed")

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

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._requests):
            request = self._requests[self._index]
            self._index += 1
            return request
        else:
            raise StopIteration

# Implementing AsyncRequestHandler
async def async_request_handler(requests):
    iterator = RequestIterator(requests)
    for request in iterator:
        print(f"Processing request asynchronously: {request}")
        await asyncio.sleep(0)  # Simulate async processing

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
        print(f"Current task list before shutting down: {tasklist}")

# Running the Web Server
def run():
    server_address = ('0.0.0.0', 9000)
    handler_class = RequestHandler
    print("Setting up server: Initializing HTTP server and handler class")

    with ServerContextManager(server_address, handler_class) as httpd:
        print("*************** Welcome to Maha's Server ***************")
        print(f"---------\nServer running at http://{server_address[0]}:{server_address[1]}\n---------")

        # Simulate some async request handling
        requests = [
            "GET / HTTP/1.1",
            "POST /tasklist/new HTTP/1.1",
            "GET /tasklist HTTP/1.1"
        ]
        asyncio.run(async_request_handler(requests))

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run()
