#!/bin/bash
LOG_FILE=/home/thuhuong/hub.log

fucntion  error_exit {
    echo "$1" 1>&2
    exit 1
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> $LOG_FILE
}

echo "Intializing master service..."
sudo systemctl start master.service || error_exit "Failed to start master service."


if [[${sudo systemctl is-active master} == "active"]]; then
    log "Master service is running successfully."

    log "Intializing gui service..."
    sudo systemctl start gui.service || error_exit "Failed to start gui service."
    log "Gui service is running successfully."

    log "Intializing ble service..."
    sudo systemctl start bluetooth.service || error_exit "Failed to start ble service."
    log "Ble service is running successfully."

    log "Intializing mqtt service..."
    sudo systemctl start mqtt.service || error_exit "Failed to start mqtt service."
    log "Mqtt service is running successfully."

    log "Intializing ai service..."
    sudo systemctl start ai.service || error_exit "Failed to start ai service."
    log "Ai service is running successfully."
else
    log "Master service failed to start. Check logs for more details."
    echo "Master service failed to start. Check logs for more details."
    sudo journalctl -u master.service --no-pager
fi