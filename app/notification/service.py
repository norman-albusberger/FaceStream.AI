import logging
import socket
import time
import requests
import os
import cv2
import csv
import json


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


class EventLogger:
    def __init__(self, log_file, base_url):
        self.log_file = log_file
        self.routePath = f"{base_url}/event-image"  # Basis-URL für Image-Paths

    def log_event(self, timestamp, name, file_name):
        # Zeit und Datum im lokalen Format formatieren
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

        # Erstellen der vollständigen URL für das Bild
        full_image_url = f"{self.routePath}/{file_name}"

        # Erstellen des Log-Eintrags als Dictionary
        log_entry = {
            "timestamp": formatted_time,
            "name": name,
            "image_path": full_image_url
        }

        # Log-Eintrag in die JSON-Datei schreiben
        with open(self.log_file, 'a') as file:
            # Anhängen des JSON-Strings am Ende der Datei mit einer Zeilenumbruch-Trennung
            file.write(json.dumps(log_entry) + '\n')

        return log_entry


class NotificationService:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.udp_service_url = config_manager.get('udp_service_url', '')
        self.udp_port = config_manager.get('udp_service_port', 0)
        self.use_udp = config_manager.get('use_udp', False)
        self.use_web = config_manager.get('use_web', False)
        self.web_service_url = config_manager.get('web_service_url', '')
        self.notification_delay = config_manager.get('notification_delay', 60)
        self.image_path = config_manager.get('image_path')
        self.log_file = config_manager.get('log_file')
        self.last_notification_time = {}

        ensure_directory(self.image_path)

    def format_custom_message(self, log_entry):
        # Abrufen der Konfiguration für die benutzerdefinierte Nachricht
        message_template = self.config_manager.get('custom_message')

        # Formatieren des Zeitstempels
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S')
        formatted_date = time.strftime('%Y-%m-%d')

        # Ersetzen der Platzhalter
        message = message_template.replace('[[name]]', log_entry['name'])
        message = message.replace('[[time]]', formatted_time.split(' ')[1])
        message = message.replace('[[date]]', formatted_date)
        message = message.replace('[[image_url]]', log_entry['image_path'])
        message = message.replace('[[timestamp]]', str(time.time()))

        logging.info(f"message: {message}")

        return message

    def notify(self, name, frame):
        current_time = time.time()
        if name not in self.last_notification_time or (
                current_time - self.last_notification_time[name]) > self.notification_delay:
            self.last_notification_time[name] = current_time
            filename, full_path = self.save_image(frame, name, current_time)
            log_entry = self.log_event(current_time, name, filename)
            if self.use_web:
                self.send_http_notification(log_entry)
            if self.use_udp:
                self.send_udp_message(log_entry)

            logging.info(
                f"Notification sent for {name} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")

    def send_udp_message(self, log_entry):
        custom_message = self.format_custom_message(log_entry).encode('utf-8')
        if self.use_udp:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(custom_message, (self.udp_service_url, self.udp_port))
                    logging.debug(f"Sent UDP message to {self.udp_service_url}:{self.udp_port}")
            except Exception as e:
                logging.error(f"Failed to send UDP message: {e}")

    def send_http_notification(self, log_entry):
        custom_message = self.format_custom_message(log_entry).encode('utf-8')
        if self.use_web:
            full_url = self.web_service_url
            try:
                response = requests.post(full_url, custom_message)
                if response.status_code == 200:
                    logging.info(f"Notification sent to HTTP endpoint {full_url} successfully.")
                else:
                    logging.error(f"Failed to send HTTP notification: {response.status_code}")
            except Exception as e:
                logging.error(f"Failed to send HTTP request: {e}")

    def save_image(self, frame, name, timestamp):
        filename = f"{name}_{int(timestamp)}.jpg"
        filepath = os.path.join(self.image_path, filename)
        cv2.imwrite(filepath, frame)
        return filename, filepath

    def log_event(self, timestamp, name, file_name):
        logger = EventLogger(self.log_file, self.config_manager.get('base_url'))
        return logger.log_event(time.time(), name, file_name)
