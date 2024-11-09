FROM ubuntu:20.04

LABEL maintainer="ynixon@gmail.com"

# Install pip3 and dependencies in a single layer to reduce image size
RUN apt-get update && \
    apt-get install -yqq python3-pip && \
    pip3 install --upgrade pip setuptools --no-cache-dir && \
    rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size

# Set environment variables for Python encoding and locale
ENV PYTHONIOENCODING="utf-8" \
    LANG="C.UTF-8" \
    DEBUG_MODE="False" \
    REGION="*" \
    INCLUDE_TEST_ALERTS="False"

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Create working directory
WORKDIR /app

# Copy application code to working directory
COPY app/ /app

# Run the application
ENTRYPOINT ["/usr/bin/python3", "/app/walert.py"]
