import cv2
import time
import face_recognition
import socket

class VideoStream:
    def __init__(self, face_loader, config_manager):
        self.config_manager = config_manager
        config_manager.load_config()
        self.video_capture = cv2.VideoCapture(config_manager.get('input_stream_url'))
        self.overlay_transparency = config_manager.get('overlay_transparency')
        self.overlay_color = config_manager.get('overlay_color')
        print(self.overlay_color)
        self.output_width = config_manager.get('output_width')
        self.output_height = config_manager.get('output_height')
        self.face_loader = face_loader

        self.notification_service_address = config_manager.get('notification_service_address')
        self.notification_service_port = config_manager.get('notification_service_port')
        self.notification_period = config_manager.get('notification_period')  # in Sekunden
        self.last_notification_time = {}
        self.face_recognition_interval = config_manager.get('face_recognition_interval')

    def draw_rectangle_with_name(self, frame, top, right, bottom, left, name):
        transparency = self.overlay_transparency

        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (right, bottom), self.overlay_color, -1)  # -1 fills the rectangle
        cv2.addWeighted(overlay, transparency, frame, 1 - transparency, 0, frame)
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    def notify_service(self, name):
        current_time = time.time()
        print(f"Gesicht erkannt:")
        print(name)
        # Prüfen, ob die Periode seit der letzten Benachrichtigung für diese Person abgelaufen ist
        if name not in self.last_notification_time or (
                current_time - self.last_notification_time[name]) > self.notification_period:
            # Aktualisieren Sie die Zeit der letzten Benachrichtigung
            self.last_notification_time[name] = current_time

            # ein UDP-Socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = name.encode('utf-8')  # Der Name der erkannten Person

            # Senden Sie die Nachricht
            sock.sendto(message, (self.notification_service_address, self.notification_service_port))
            sock.close()

    def generate_frames(self):
        frame_counter = 0
        face_recognition_interval = 60  # Führe die Gesichtserkennung alle 5 Frames durch

        while True:
            start_time = time.time()
            # Versuchen, einen Frame zu lesen; wenn fehlgeschlagen, überspringe die aktuelle Iteration der Schleife
            ret, frame = self.video_capture.read()
            if not ret or frame is None:
                elapsed_time = time.time() - start_time
                if elapsed_time > 30:  # 30 Sekunden Timeout
                    print(f"Timeout: Das Lesen des Frames dauerte {elapsed_time} Sekunden.")
                else:
                    print("Fehler: Frame konnte nicht gelesen werden oder ist leer.")
                continue

            try:
                frame = cv2.resize(frame, (self.output_width, self.output_height))
            except cv2.error as e:
                print(f"OpenCV Fehler beim Skalieren des Frames: {e}")
                continue  # Überspringt den Rest der aktuellen Iteration und fährt mit der nächsten Iteration fort

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            if frame_counter % face_recognition_interval == 0:
                try:
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                except Exception as e:
                    print(f"Fehler bei der Gesichtserkennung: {e}")
                    continue  # Überspringt den Rest der aktuellen Iteration und fährt mit der nächsten Iteration fort

            frame_counter += 1

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                matches = face_recognition.compare_faces(self.face_loader.known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.face_loader.known_face_names[first_match_index]

                    if self.config_manager.get('enable_notification_service'):
                        self.notify_service(name)

                # Reskaliere die Positionen der Gesichter
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                self.draw_rectangle_with_name(frame, top, right, bottom, left, name)

            try:
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                if not flag:
                    print("Fehler beim Kodieren des Frames.")
                    continue
            except Exception as e:
                print(f"Fehler beim Kodieren des Frames: {e}")
                continue

            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
