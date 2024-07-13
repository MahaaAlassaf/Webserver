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

## Setup and Installation

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

To run the server, execute the following command:

```bash
python webserver.py
