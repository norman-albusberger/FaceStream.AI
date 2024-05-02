import cv2
import threading
import logging
from queue import Full
import time


class CameraManager(threading.Thread):
    def __init__(self, frame_queue, camera_url, output_size=(640, 480), max_retries=5):
        super().__init__()
        self.camera_url = camera_url
        self.output_size = output_size
        self.frame_queue = frame_queue
        self.capture = None
        self.running = True
        self.max_retries = max_retries  # Maximale Anzahl von Verbindungsversuchen

    def open_camera(self):
        attempt = 0
        while attempt < self.max_retries and not self.capture:
            self.capture = cv2.VideoCapture(self.camera_url)
            if self.capture.isOpened():
                logging.info("Kamera erfolgreich verbunden.")
                return
            else:
                logging.warning(f"Kann Kamera nicht öffnen, Versuch {attempt + 1}/{self.max_retries}")
                attempt += 1
                self.capture.release()
                self.capture = None
                time.sleep(2)  # Wartezeit zwischen den Versuchen
        if not self.capture:
            logging.error("Kamera konnte nach mehreren Versuchen nicht geöffnet werden.")
            raise ValueError("Kamera konnte nicht geöffnet werden")

    def run(self):
        self.open_camera()
        while self.running:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    resized_frame = cv2.resize(frame, self.output_size)
                    try:
                        self.frame_queue.put(resized_frame,
                                             timeout=0.05)

                    except Full:
                        logging.error("Frame queue ist voll. Ältere Frames werden verworfen.")
                else:
                    logging.error("Kein Frame empfangen, Kamera neu verbinden.")
                    self.close_camera()
                    self.open_camera()
            else:
                logging.warning("Warnung: Kamera konnte kein Frame erfassen")
        else:
            logging.error("Kamera ist nicht geöffnet. Versuch, die Kamera neu zu öffnen")
            self.open_camera()

    def stop(self):
        self.running = False
        self.close_camera()
        logging.info("CameraManager gestoppt und Ressourcen freigegeben.")

    def close_camera(self):
        if self.capture:
            self.capture.release()
            self.capture = None
            logging.info("Kamera-Verbindung wurde geschlossen.")


def set_output_size(self, width, height):
    self.output_size = (width, height)