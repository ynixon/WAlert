# WAlert
WAlert is a real-time alert monitoring bot that checks for Red Alert notifications from the Oref website and sends them to designated WhatsApp numbers using the Green API. This tool is ideal for users who need immediate notifications for specific regions in Israel, with options to include or exclude test alerts.

## Overview
WAlert is a Python-based bot that monitors alert notifications from the [Oref](https://www.oref.org.il/heb) website and forwards them via WhatsApp using the [Green API](https://green-api.com/). The bot categorizes and formats alerts, sending them to designated WhatsApp numbers in real-time. You can configure it to monitor specific regions and choose whether or not to receive test alerts.

## Prerequisites
* Python 3.10+ (for manual installation)
* Docker (for containerized installation)

## Installation Options
You can install WAlert using either a Docker container or set it up as a systemd service for manual deployment.

### Option 1: Docker Installation

1. **Pull the Docker Image**  
   Pull the pre-built Docker image from Docker Hub:
   ```bash
   docker pull ynixon/walert:latest
   ```

2. **Run the Docker Container with Secrets**  
   To run the container securely, use environment variables for non-sensitive data and provide sensitive data at runtime:
   ```bash
   docker run -d \
       -e DEBUG_MODE="False" \
       -e REGION="*" \
       -e INCLUDE_TEST_ALERTS="False" \
       -e GREEN_API_INSTANCE="your_green_api_instance" \
       -e WHATSAPP_NUMBER="your_whatsapp_number" \
       --name walert ynixon/walert:latest
   ```
   Provide `GREEN_API_TOKEN` at runtime:
   ```bash
   GREEN_API_TOKEN="your_green_api_token" docker run -d \
       -e DEBUG_MODE="False" \
       -e REGION="*" \
       -e INCLUDE_TEST_ALERTS="False" \
       -e GREEN_API_INSTANCE="your_green_api_instance" \
       -e WHATSAPP_NUMBER="your_whatsapp_number" \
       ynixon/walert:latest
   ```

3. **Using Docker Compose**  
   You can also use `docker-compose` for more complex setups or for easier management. To use secrets securely with Docker Compose, ensure that `GREEN_API_TOKEN` is stored as an external secret in your Docker environment:
   ```yaml
   version: "3.6"
   services:
     walert:
       image: ynixon/walert:latest
       container_name: walert
       restart: always
       environment:
         DEBUG_MODE: "False"
         REGION: "*"
         INCLUDE_TEST_ALERTS: "False"
         GREEN_API_INSTANCE: "your_green_api_instance"
         WHATSAPP_NUMBER: "your_whatsapp_number"
       secrets:
         - GREEN_API_TOKEN

   secrets:
     GREEN_API_TOKEN:
       external: true
   ```
   To run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Option 2: Manual Installation (Systemd Service)

1. **Clone the Repository or Download the ZIP Package**
   ```bash
   # Clone via Git
   git clone https://github.com/ynixon/walert.git
   cd walert

   # Alternatively, download and extract the ZIP package
   curl -LO https://github.com/ynixon/walert/archive/main.zip
   unzip main.zip
   cd walert-main
   ```

2. **Install Python Dependencies**
   Ensure you have Python 3.10+ installed. Use pip to install the dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a .env File**
   In the root directory, create a `.env` file to configure non-sensitive environment variables. For sensitive data, such as `GREEN_API_TOKEN`, provide it securely at runtime.
   ```makefile
   DEBUG_MODE=False
   REGION=*
   INCLUDE_TEST_ALERTS=False
   GREEN_API_INSTANCE=your_green_api_instance
   WHATSAPP_NUMBER=your_whatsapp_number
   ```

4. **Create a Systemd Service**
   Configure the bot as a systemd service:
   ```bash
   sudo nano /etc/systemd/system/walert.service
   ```
   Add the following configuration:
   ```ini
   [Unit]
   Description=WAlert - WhatsApp bot for Red Alert alarms
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/walert
   EnvironmentFile=/path/to/walert/.env
   ExecStart=/usr/bin/python3 /path/to/walert/main.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   Replace `/path/to/walert` with your WAlert directory path and `your-username` with your system username.

   Reload systemd, enable, and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable walert
   sudo systemctl start walert
   ```
   Check the service status:
   ```bash
   sudo systemctl status walert
   ```

## Environment Variables

* **DEBUG_MODE**: Enable test mode to simulate alerts (default: False).
* **REGION**: Specify the region for monitoring (`*` for all regions).
* **INCLUDE_TEST_ALERTS**: Include test alerts from Oref (default: False).
* **GREEN_API_INSTANCE**: Your Green API instance ID.
* **GREEN_API_TOKEN**: Your Green API token for authentication. **Do not store this directly in the Dockerfile**.
* **WHATSAPP_NUMBER**: The WhatsApp number where alerts will be sent.
    - For contacts, the number should end with `@c.us`
    - For groups, the number should end with `@g.us`

Refer to the [Green API documentation](https://green-api.com/en/docs/) for more information.