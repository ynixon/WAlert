# WAlert
A WhatsApp bot for sending Red Alert notifications using the Green API.


## Overview
WAlert is a Python-based bot that monitors alert notifications from the [Oref](https://www.oref.org.il/heb) Website and forwards them via WhatsApp using the [Green API](https://green-api.com/). The bot categorizes and formats alerts, sending them to designated WhatsApp numbers in real-time. You can configure it to monitor specific regions and choose whether or not to receive test alerts.


## Prerequisites
* Python 3.10+ (For manual installation)
* Docker (For containerized installation)

## Installation Options
You can install WAlert using either a Docker container or set it up as a systemd service for manual deployment.

### Option 1: Docker Installation

1. Pull the Docker Image
Pull the pre-built Docker image from Docker Hub:

```bash
docker pull techblog/walert:latest
```

2. Run the Docker Container
Run the Docker container with your required environment variables:

```bash
docker run -d \
    -e DEBUG_MODE="False" \
    -e REGION="*" \
    -e INCLUDE_TEST_ALERTS="False" \
    -e GREEN_API_INSTANCE="your_green_api_instance" \
    -e GREEN_API_TOKEN="your_green_api_token" \
    -e WHATSAPP_NUMBER="your_whatsapp_number" \
    --name walert your-dockerhub-user/walert:latest
```

3. Docker Compose.
You can also use docker-compose for more complex setups or for easier management:

```yaml
version: "3.6"
services:
  walert:
    image: your-dockerhub-user/walert:latest
    container_name: walert
    restart: always
    environment:
      - DEBUG_MODE=False
      - REGION=*
      - INCLUDE_TEST_ALERTS=False
      - GREEN_API_INSTANCE=your_green_api_instance
      - GREEN_API_TOKEN=your_green_api_token
      - WHATSAPP_NUMBER=your_whatsapp_number
```

To run with docker-compose:
```bash
docker-compose up -d
```

### Option 2: Manual Installation (Systemd Service)

1. Clone the Repository or Download the ZIP Package. 
You can clone the repository from GitHub or download the ZIP package:

```bash
# Clone via Git
git clone https://github.com/your-repo/walert.git
cd walert

# Alternatively, download and extract the ZIP package
curl -LO https://github.com/your-repo/walert/archive/main.zip
unzip main.zip
cd walert-main
```

2. Install Python Dependencies. Ensure you have Python 3.10+ installed. Use pip to install the dependencies listed in requirements.txt:

```bash
pip install -r requirements.txt
```

3. Create a .env File  file in the root directory to configure environment variables. This file will contain sensitive information like your Green API credentials and WhatsApp number.

```bash
touch .env
```

Add the following to your .env file:

```makefile
DEBUG_MODE=False
REGION=*
INCLUDE_TEST_ALERTS=False
GREEN_API_INSTANCE=your_green_api_instance
GREEN_API_TOKEN=your_green_api_token
WHATSAPP_NUMBER=your_whatsapp_number
```

4. Create a Systemd Service: To run the bot automatically as a service, you can configure it as a systemd service.

    * Create a new service file:
    ```bash
    sudo nano /etc/systemd/system/walert.service
    ```
     * Add the following configuration:
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
    * Replace /path/to/walert with the actual path to your WAlert directory and your-username with your system username.

    * Reload systemd, enable, and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable walert
    sudo systemctl start walert
    ```
    * Check the service status:
    ```bash
    sudo systemctl status walert
    ```


## Environment Variables
* **DEBUG_MODE:** Enable test mode to simulate alerts (default: False).
* **REGION:** Specify the region for monitoring (* for all regions).
* **INCLUDE_TEST_ALERTS:** Include test alerts from Oref (default: False).
* **GREEN_API_INSTANCE:** Your Green API instance ID.
* **GREEN_API_TOKEN:** Your Green API token for authentication.
* **WHATSAPP_NUMBER:** The WhatsApp number where alerts will be sent. 
    * For contacts the number should end with @c.us
    * For groups the number should end with @g.us

You can find the full documentation here on the [Green API](https://green-api.com/en/docs/) website.