# What is this?

This is the backend for the Pyright playground

It has a single enpoint `/pyright` which accepts a POST request.
The request must have a JSON object with a single field `"code"` containing
the Python code as a string.


# How to run this?

1. Install Python 3.10
2. Install Poetry
3. `poetry install`
4. `uvicorn app:app`
