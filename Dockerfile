FROM python:3.9-buster

# Install Node
RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
RUN sh /tmp/nodesource_setup.sh
RUN apt install -yq nodejs
RUN node -v

# Install poetry
RUN pip install poetry

# Build frontend

# <TODO> figure out why rollup -c hangs

# COPY frontend /src/frontend
# WORKDIR /src/frontend
# RUN npm i
# RUN npm run build
# RUN mkdir -p /build/frontend
# RUN cp -r /src/frontend/public /build/frontend
# RUN rm -rf /src/frontend

COPY frontend/public /build/frontend
ENV STATIC_PATH /build/frontend

# Build backend
RUN mkdir -p /src/backend
WORKDIR /src/backend
COPY backend/pyproject.toml /src/backend/pyproject.toml
COPY backend/poetry.lock /src/backend/poetry.lock
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt
RUN pip install -r requirements.txt
COPY backend /src/backend/

# Run server
WORKDIR /src/backend
CMD python -m uvicorn backend.app:app --host 0.0.0.0 --port 3000
