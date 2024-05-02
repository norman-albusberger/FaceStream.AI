import threading
import time
import signal
import logging
import os
from flask import Flask, Response, stream_with_context
import cv2
import queue




def check_for_restart_signal(signal_file_path, interval=10):
    while True:
        if os.path.exists(signal_file_path):
            logging.info("Signaldatei gefunden. Server wird neu gestartet...")
            os.remove(signal_file_path)
            os.kill(os.getpid(), signal.SIGTERM)
        time.sleep(interval)


class VideoStreamingServer:
    def __init__(self, config_manager, frame_queue):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.frame_queue = frame_queue  # Die Warteschlange für Frames
        self.define_routes()
        self.last_request_time = time.time()
        self.active_clients = 0
        self.client_lock = threading.Lock()
        signal_file_path = 'data/signal_file'
        restart_thread = threading.Thread(target=check_for_restart_signal, args=(signal_file_path,))
        restart_thread.daemon = True
        restart_thread.start()

    def define_routes(self):
        @self.app.route('/stream')
        def video_feed():
            with self.client_lock:
                if self.active_clients == 0:
                    generator = self.start_stream()
                self.active_clients += 1

            def stream():
                try:
                    logging.info("stream gestartet")
                    for frame_chunk in generator:
                        yield frame_chunk
                except Exception as e:
                    logging.error(f"Error during frame generation: {e}")
                finally:
                    with self.client_lock:
                        self.active_clients -= 1
                        if self.active_clients == 0:
                            self.stop_stream()

            return Response(stream_with_context(stream()), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start_stream(self):
        def generate():
            while True:
                try:
                    # Blockiert, bis ein Frame verfügbar ist oder ein Timeout erreicht ist
                    frame = self.frame_queue.get(timeout=1)

                    # Verwerfe alle älteren Frames, die sich noch in der Queue befinden
                    while not self.frame_queue.empty():
                        try:
                            # Versuche, den nächsten Frame zu holen, falls verfügbar
                            frame = self.frame_queue.get_nowait()
                        except queue.Empty:
                            break

                    if frame is None or frame.size == 0:
                        logging.error("Leeres oder ungültiges Frame erhalten")
                        continue

                    _, jpeg = cv2.imencode('.jpg', frame)
                    if jpeg is None:
                        logging.error("Fehler beim Kodieren des Frames")
                        continue

                    frame_data = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                    # Die Wartezeit wird entfernt, da wir stets das neueste Frame so schnell wie möglich senden wollen
                except queue.Empty:
                    logging.debug("Warte auf Frames...")
                except Exception as e:
                    logging.error(f"Error during frame generation: {e}")

        return generate()

    def stop_stream(self):
        logging.info("stream gestoppt")

    def run(self):
        self.app.run(host='0.0.0.0', port=5001, threaded=True, use_reloader=False)
