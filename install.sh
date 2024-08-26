#!/bin/bash

# Function to display a message and exit on error
function error_exit {
    echo "$1" 1>&2
    exit 1
}

# Update system package index
echo "Updating package index..."
sudo apt-get update || error_exit "Failed to update package index."

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y build-essential cmake portaudio19-dev || error_exit "Failed to install system dependencies."
sudo apt-get install -y portaudio19-dev flac || error_exit "Failed to install system dependencies."
sudo apt-get install -y espeak libespeak1 libespeak-dev || error_exit "Failed to install audio dependencies."
sudo apt install bluez || error_exit "Failed to install ble dependencies."
pip install --no-cache-dir SpeechRecognition || error_exit "Failed to install speech recogniton dependencies."
python -m pip install cohere --upgrade error_exit "Failed to install speech recogniton dependencies."

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt || error_exit "Failed to install Python dependencies."
else
    error_exit "requirements.txt not found."
fi

# Enable and start services
# services=("ble" "mqtt" "graphici_interface")
# for service in "${services[@]}"; do
#     echo "Enabling and starting $service.service..."
#     sudo systemctl enable "$service.service" || error_exit "Failed to enable $service.service."
#     sudo systemctl start "$service.service" || error_exit "Failed to start $service.service."
# done

# # Check status of each service
# for service in "${services[@]}"; do
#     echo "Checking status of $service.service..."
#     sudo systemctl status "$service.service" --no-pager
#     if ! sudo systemctl is-active --quiet "$service.service"; then
#         echo "$service.service failed to start. Check logs for more details."
#         sudo journalctl -u "$service.service" --no-pager
#     else
#         echo "$service.service is running successfully."
#     fi
# done

echo "Installation and configuration completed successfully."
