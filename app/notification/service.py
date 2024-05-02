import logging
import socket
import time

class NotificationService:
    def __init__(self, service_address, service_port, notification_period):
        self.service_address = service_address
        self.service_port = service_port
        self.notification_period = notification_period  # in seconds
        self.last_notification_time = {}

    def notify(self, name):
        current_time = time.time()
        logging.info(f"Gesicht erkannt: {name}")
        #
        #if name not in self.last_notification_time or (
        #        current_time - self.last_notification_time[name]) > self.notification_period:
        #    self.last_notification_time[name] = current_time
        #    self.send_udp_message(name)

    def send_udp_message(self, name):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                message = name.encode('utf-8')
                sock.sendto(message, (self.service_address, self.service_port))
                logging.info(f"Sent message to {self.service_address}:{self.service_port}")
        except Exception as e:
            logging.debug(f"Failed to send UDP message: {e}")

