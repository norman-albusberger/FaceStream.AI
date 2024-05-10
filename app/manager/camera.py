import cv2
import threading
import logging
import time
import queue


class CameraManager(threading.Thread):
    def __init__(self, frame_queue, camera_url, output_size=(640, 480), max_retries=15):
        super().__init__()
        self.camera_url = camera_url
        self.output_size = output_size
        self.frame_queue = frame_queue
        self.capture = None
        self.running = True
        self.max_retries = max_retries  # Maximale Anzahl von Verbindungsversuchen

    def open_camera(self):
        if not self.camera_url:  # Überprüfe, ob die Kamera-URL leer ist
            logging.error("Keine Kamera-URL angegeben.")
            raise ValueError("Keine Kamera-URL angegeben")
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
                    while True:
                        try:
                            self.frame_queue.put(resized_frame, timeout=0.05)
                            break  # Frame erfolgreich hinzugefügt, Schleife verlassen
                        except queue.Full:
                            try:
                                # Versuche, den ältesten Frame zu entfernen, um Platz zu schaffen
                                self.frame_queue.get_nowait()
                                logging.info("Frame queue ist voll. Ältester Frame wurde verworfen.")
                            except queue.Empty:
                                # Sollte normalerweise nicht passieren, da wir wissen, dass die Queue voll ist
                                logging.error("Versuch, aus leerer Queue zu lesen. Das sollte nicht passieren.")
                else:
                    logging.error("Kein Frame empfangen, Kamera neu verbinden.")
                    self.close_camera()
                    self.open_camera()
            else:
                logging.error("Kamera ist nicht geöffnet. Versuch, die Kamera neu zu öffnen.")
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
