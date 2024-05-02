import logging
import socket
import time
import requests  # Für HTTP-Requests
import os
import cv2
import csv


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


class NotificationService:
    def __init__(self, service_address, service_port, notification_period, image_save_path, log_path):
        self.service_address = service_address
        self.service_port = service_port
        self.notification_period = notification_period  # in seconds
        self.last_notification_time = {}
        self.image_save_path = image_save_path
        ensure_directory(self.image_save_path)
        self.log_path = log_path

    def notify(self, name, frame):
        current_time = time.time()
        if name not in self.last_notification_time or (
                current_time - self.last_notification_time[name]) > self.notification_period:
            self.last_notification_time[name] = current_time
            image_path = self.save_image(frame, name, current_time)
            self.send_http_notification(name)
            self.send_udp_message(name)
            self.log_event(current_time, name, image_path)
            logging.info(
                f"Notification sent for {name} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")

    def log_event(self, timestamp, name, image_path):
        with open(self.log_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)), name, image_path])

    def send_udp_message(self, name):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                message = f"Alert: {name}".encode('utf-8')
                sock.sendto(message, (self.service_address, self.service_port))
                logging.info(f"Sent UDP message to {self.service_address}:{self.service_port}")
        except Exception as e:
            logging.error(f"Failed to send UDP message: {e}")

    def send_http_notification(self, name):
        try:
            response = requests.post("http://example.com/api/notify", json={"name": name})
            if response.status_code == 200:
                logging.info("Notification sent to HTTP endpoint successfully.")
            else:
                logging.error(f"Failed to send HTTP notification: {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to send HTTP request: {e}")

    def save_image(self, frame, name, timestamp):
        filename = f"{name}_{int(timestamp)}.jpg"
        filepath = os.path.join(self.image_save_path, filename)
        cv2.imwrite(filepath, frame)
        return filepath
