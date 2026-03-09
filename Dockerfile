FROM ubuntu:26.04

LABEL maintainer="ynixon@gmail.com"

# Install Python and create a virtual environment
RUN apt-get update && \
    apt-get install -yqq python3 python3-venv python3-pip && \
    python3 -m venv /opt/venv && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools --no-cache-dir

# Set environment variables for Python encoding and locale
ENV PYTHONIOENCODING="utf-8" \
    LANG="C.UTF-8" \
    LOG_LEVEL="INFO" \
    REGION="*" \
    INCLUDE_TEST_ALERTS="False"

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Create working directory
WORKDIR /app

# Copy application code to working directory
COPY app/ /app

# Run the application
ENTRYPOINT ["python", "/app/walert.py"]
