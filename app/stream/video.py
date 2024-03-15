import cv2
import time
import face_recognition


class VideoStream:
    def __init__(self, input_stream_url, overlay_color, overlay_transparency, output_width, output_height, face_loader):
        self.video_capture = cv2.VideoCapture(input_stream_url)
        self.overlay_transparency = overlay_transparency
        self.overlay_color = overlay_color
        print(self.overlay_color)
        self.output_width = output_width
        self.output_height = output_height
        self.face_loader = face_loader

    def draw_rectangle_with_name(self, frame, top, right, bottom, left, name):
        transparency = self.overlay_transparency

        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (right, bottom), self.overlay_color, -1)  # -1 fills the rectangle
        cv2.addWeighted(overlay, transparency, frame, 1 - transparency, 0, frame)
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    def generate_frames(self):
        fps_limit = 10
        time_per_frame = 1.0 / fps_limit
        last_time = 0

        while True:
            ret, frame = self.video_capture.read()
            frame = cv2.resize(frame, (self.output_width, self.output_height))

            if not ret:
                break

            current_time = time.time()
            if current_time - last_time < time_per_frame:
                continue

            last_time = current_time

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                matches = face_recognition.compare_faces(self.face_loader.known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.face_loader.known_face_names[first_match_index]

                # rescale face_locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                self.draw_rectangle_with_name(frame, top, right, bottom, left, name)

            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
