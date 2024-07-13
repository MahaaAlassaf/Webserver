# Web Server with Advanced Python Features

## Overview

This project demonstrates the creation of a basic web server using Python that handles HTTP requests and generates appropriate responses, including streaming responses using generators. It showcases various advanced Python features such as decorators, generators, iterators, coroutines & async iterators, inheritance, polymorphism, context managers, and the singleton pattern.

## Features

1. **Logging requests using decorators**
2. **Authorizing requests using decorators**
3. **Handling requests with a base handler class and derived GET and POST handler classes**
4. **Generating streaming responses**
5. **Managing multiple requests using iterators**
6. **Asynchronously handling requests**
7. **Managing the server lifecycle with context managers**
8. **Ensuring a single instance of the server using the singleton pattern**

## Key Implementations and Smart Features

This web server is designed to handle HTTP requests efficiently and securely while demonstrating advanced Python programming techniques:

1. **Authorization and Logging:**
    - Every incoming request is first checked for authorization using the `authorize_request` decorator, ensuring that only authorized requests are processed. This enhances the security of the server.
    - The `log_request` decorator logs details of each request, such as the request path and client address. This is useful for debugging and monitoring the server's activity.

2. **Streaming Responses:**
    - To handle large responses efficiently, the server uses the `streaming_response_generator`. This generator function breaks down the response into smaller chunks and sends them incrementally. This reduces memory usage and ensures that large payloads do not overwhelm the server.

3. **Request Management:**
    - The server manages multiple incoming requests using the `RequestIterator` class, which implements the iterator protocol. This ensures that requests are processed sequentially in a controlled manner.

4. **Asynchronous Request Handling:**
    - The server improves its responsiveness and scalability by handling multiple requests asynchronously. The `async_request_handler` function processes requests using coroutines and async iterators, allowing the server to handle concurrent operations more effectively.

5. **Modular and Extensible Request Handlers:**
    - The server uses a modular design with a base class `BaseRequestHandler` for handling requests. Specific request types, such as GET and POST, are handled by derived classes `GetRequestHandler` and `PostRequestHandler`. This demonstrates inheritance and polymorphism, making the server easy to extend and maintain.

6. **Server Lifecycle Management:**
    - The `ServerContextManager` class ensures proper resource management during the server's lifecycle. It handles initialization and shutdown processes, ensuring that the server starts and stops cleanly.

7. **Singleton Pattern for Server Instance Management:**
    - The `WebServer` class implements the singleton pattern to ensure that only one instance of the server is running at any time. This prevents conflicts that could arise from multiple instances running simultaneously.
