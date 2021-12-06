# What is this?

This is the backend for the Pyright playground

It has a single enpoint `/pyright` which accepts a POST request.
The request must have a JSON object with a single field `"code"` containing
the Python code as a string.


# How to run this?

1. Install Node.js and `npm`
2. Go to `lang-server/`
3. Run `npm i
4. Go back
5. Install Python 3.9 or later
6. Install Poetry
7. `poetry install`
8. `uvicorn app:app`
