# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY data/python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all scripts and data from data/ into /
COPY data/. .

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1

# Set the working directory to where the Python script is located
WORKDIR /python

# Set the entrypoint to run the CLI with any passed arguments
ENTRYPOINT ["python", "twowords_cli.py"]
