import config
import cv2
import numpy as np
from flask import Flask, Response, render_template
import face_recognition
from Lib import FaceRecognition
import time


class VideoStreamApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.face_recognition = FaceRecognition()
        self.define_routes()

    def define_routes(self):
        @self.app.route(config.OUTPUT_PATH)
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/')
        def guide():
            return render_template('index.html', stream_url=config.INPUT_STREAM_URL, host_ip=config.OUTPUT_HOST,
                                   port=config.OUTPUT_PORT,
                                   video_path=config.OUTPUT_PATH)

    def draw_rectangle_with_name(self, frame, top, right, bottom, left, name):
        # Definieren der Transparenz (zwischen 0 und 1)
        transparency = config.OVERLAY_TRANSPARENCY
        print(transparency)

        # Erstellen eines Overlay, um die Transparenz zu simulieren
        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (right, bottom), (220, 220, 200), -1)  # -1 füllt das Rechteck aus

        # Kombinieren des Overlays mit dem Originalbild, um die Transparenz zu simulieren
        cv2.addWeighted(overlay, transparency, frame, 1 - transparency, 0, frame)

        # Schreibe den Namen des Gesichts unter das Rechteck
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    def generate_frames(self):
        video_capture = cv2.VideoCapture(config.INPUT_STREAM_URL)

        fps_limit = 10  # Ziel-Frame-Rate
        time_per_frame = 1.0 / fps_limit
        last_time = 0

        while True:
            ret, frame = video_capture.read()
            frame = cv2.resize(frame, (config.OUTPUT_WIDTH, config.OUTPUT_HEIGHT))  # Beispiel für angepasste Größe

            if not ret:
                break

            current_time = time.time()
            if current_time - last_time < time_per_frame:
                continue  # Überspringt die Verarbeitung dieses Frames

            last_time = current_time

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                matches = face_recognition.compare_faces(self.face_recognition.known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.face_recognition.known_face_names[first_match_index]

                # Skaliere die Gesichtspositionen zurück, da das Frame verkleinert wurde
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Rufe die Methode zum Zeichnen des Rechtecks und des Namens auf
                self.draw_rectangle_with_name(frame, top, right, bottom, left, name)

            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'

    def run(self):
        self.app.run(host=config.OUTPUT_HOST, port=config.OUTPUT_PORT, threaded=True, use_reloader=False)


if __name__ == '__main__':
    video_stream_app = VideoStreamApp()
    video_stream_app.run()
