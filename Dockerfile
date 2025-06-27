# FROM python:3.10-slim

# WORKDIR /code

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .
FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt .

# Add a longer timeout and retry for pip install
RUN pip install --default-timeout=100 --retries=10 --no-cache-dir -r requirements.txt

COPY . .

