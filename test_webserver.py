import unittest
from unittest.mock import MagicMock, patch
from http.server import BaseHTTPRequestHandler
import asyncio
from iterators import RequestHandler
from webserver import (log_request, authorize_request, GetRequestHandler, PostRequestHandler, 
                       ShutdownRequestHandler, streaming_response_generator, RequestIterator, 
                       AsyncRequestIterator, async_request_handler, WebServer, 
                       ServerContextManager)

# Test Decorators
class TestDecorators(unittest.TestCase):
    def test_log_request(self):
        print("Running TestDecorators.test_log_request")
        @log_request
        def mock_func(self):
            return "called"
        
        mock_handler = MagicMock()
        mock_handler.client_address = ('127.0.0.1', 8080)
        mock_handler.path = '/'
        
        result = mock_func(mock_handler)
        self.assertEqual(result, "called")
        print("TestDecorators.test_log_request passed\n")

    def test_authorize_request(self):
        print("Running TestDecorators.test_authorize_request")
        @authorize_request
        def mock_func(self):
            return "authorized"
        
        mock_handler = MagicMock()
        mock_handler.client_address = ('127.0.0.1', 8080)
        mock_handler.path = '/'
        
        result = mock_func(mock_handler)
        self.assertEqual(result, "authorized")
        print("TestDecorators.test_authorize_request passed\n")

# Test Generators
class TestGenerators(unittest.TestCase):
    def test_streaming_response_generator(self):
        print("Running TestGenerators.test_streaming_response_generator")
        message = "This is a test message."
        chunks = list(streaming_response_generator(message))
        self.assertEqual("".join(chunks), message)
        print("TestGenerators.test_streaming_response_generator passed\n")

# Test Iterators
class TestRequestIterator(unittest.TestCase):
    def test_request_iterator(self):
        print("Running TestRequestIterator.test_request_iterator")
        requests = ["request1", "request2", "request3"]
        iterator = RequestIterator(requests)
        self.assertEqual(len(iterator), 3)
        self.assertEqual(list(iterator), requests)
        print("TestRequestIterator.test_request_iterator passed\n")

class TestAsyncRequestIterator(unittest.IsolatedAsyncioTestCase):
    async def test_async_request_iterator(self):
        print("Running TestAsyncRequestIterator.test_async_request_iterator")
        requests = ["request1", "request2", "request3"]
        iterator = AsyncRequestIterator(RequestIterator(requests))
        result = [req async for req in iterator]
        self.assertEqual(result, requests)
        print("TestAsyncRequestIterator.test_async_request_iterator passed\n")

class TestAsyncRequestHandler(unittest.IsolatedAsyncioTestCase):
    async def test_async_request_handler(self):
        print("Running TestAsyncRequestHandler.test_async_request_handler")
        requests = ["request1", "request2", "request3"]
        iterator = RequestIterator(requests)
        
        await async_request_handler(iterator)
        print("TestAsyncRequestHandler.test_async_request_handler passed\n")

class TestGetRequestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = GetRequestHandler()

    def test_handle_request(self):
        print("Running TestGetRequestHandler.test_handle_request")
        mock_handler = MagicMock(spec=BaseHTTPRequestHandler)
        mock_handler.client_address = ('127.0.0.1', 8080)
        mock_handler.headers = {
            'User-Agent': 'TestAgent',
            'Content-Type': 'application/json'
        }
        mock_handler.path = '/'  
        mock_handler.wfile = MagicMock()
        
        self.handler.handle_request(mock_handler)
        
        mock_handler.wfile.write.assert_called()
        print("TestGetRequestHandler.test_handle_request passed\n")

class TestPostRequestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = PostRequestHandler()

    def test_handle_request(self):
        print("Running TestPostRequestHandler.test_handle_request")
        mock_handler = MagicMock(spec=BaseHTTPRequestHandler)
        mock_handler.client_address = ('127.0.0.1', 8080)
        mock_handler.headers = {
            'User-Agent': 'TestAgent',
            'Content-Length': '50',
            'Content-Type': 'application/json'
        }
        mock_handler.rfile = MagicMock()
        mock_handler.rfile.read = MagicMock(return_value=b'task=sample_task')
        mock_handler.path = '/'  
        mock_handler.wfile = MagicMock()
        
        self.handler.handle_request(mock_handler)
        
        mock_handler.wfile.write.assert_called()
        print("TestPostRequestHandler.test_handle_request passed\n")

class TestShutdownRequestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ShutdownRequestHandler()

    def test_handle_request(self):
        print("Running TestShutdownRequestHandler.test_handle_request")
        mock_handler = MagicMock(spec=BaseHTTPRequestHandler)
        mock_handler.server = MagicMock()
        mock_handler.wfile = MagicMock()
        
        self.handler.handle_request(mock_handler)
        
        mock_handler.server.shutdown.assert_called_once()
        print("TestShutdownRequestHandler.test_handle_request passed\n")

class TestWebServer(unittest.TestCase):
    def test_singleton(self):
        print("Running TestWebServer.test_singleton")
        server1 = WebServer(('0.0.0.0', 9000), RequestHandler)
        server2 = WebServer(('0.0.0.0', 9000), RequestHandler)
        self.assertIs(server1, server2)
        print("TestWebServer.test_singleton passed\n")

class TestServerContextManager(unittest.TestCase):
    def test_context_manager(self):
        print("Running TestServerContextManager.test_context_manager")
        with patch('webserver.HTTPServer') as MockHTTPServer:
            MockHTTPServer.return_value = MagicMock()
            with ServerContextManager(('0.0.0.0', 9000), RequestHandler) as server:
                self.assertIsInstance(server, MagicMock)
        print("TestServerContextManager.test_context_manager passed\n")

if __name__ == '__main__':
    unittest.main()

