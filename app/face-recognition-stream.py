import os
import face_recognition
import cv2
import numpy as np
from flask import Flask, Response, render_template, request
from datetime import datetime

# Configuration from environment variables
INPUT_STREAM_URL = os.getenv('INPUT_STREAM_URL', '/dev/video0')
OUTPUT_HOST = os.getenv('OUTPUT_HOST', '0.0.0.0')
OUTPUT_PORT = int(os.getenv('OUTPUT_PORT', '5000'))
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/video')
IMAGE_DIRECTORY = os.getenv('IMAGE_DIRECTORY', '/default/path/if/not/set')
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL')

app = Flask(__name__)

# Lists to store known face encodings and names
known_face_encodings = []
known_face_names = []

# Iterate through all files in the directory
imageDir = os.listdir(IMAGE_DIRECTORY)
for filename in imageDir:
    print("Known Faces are :\n")
    print(filename + "\n")

    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith(
            '.png'):  # Check if the file is an image
        # Path to the image file
        file_path = os.path.join(IMAGE_DIRECTORY, filename)

        # Load the image and learn to recognize it
        image = face_recognition.load_image_file(file_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            # Assume the first face encoding (if multiple faces in the image, only the first one is considered)
            face_encoding = face_encodings[0]

            # Add the face encoding and the filename (without file extension) to the list
            known_face_encodings.append(face_encoding)
            known_face_names.append(os.path.splitext(filename)[0])  # Remove the file extension for the name

# Now 'known_face_encodings' and 'known_face_names' contain the encodings and names of all recognized faces

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def notify_service(name_detected):
    url = NOTIFICATION_SERVICE_URL  # Verwenden der Umgebungsvariable
    data = {
        "name": name_detected,
        "timestamp": datetime.now().isoformat()
    }
    try:
        response = request.post(url, json=data)
        response.raise_for_status()  # Stellt sicher, dass eine erfolgreiche Antwort vorliegt
    except request.RequestException as e:
        print(f"Error while sending data for notify_service: {e}")


frame_count = 0  # Zählvariable initialisieren
n = 5  # Nur jeder 5. Frame wird für die Gesichtserkennung verwendet


def generate_frames():
    video_capture = cv2.VideoCapture(INPUT_STREAM_URL)
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Bildgröße anpassen, Seitenverhältnis beibehalten
        frame = cv2.resize(frame, (1280, 960))  # Beispiel für angepasste Größe

        if frame_count % n == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

            if NOTIFICATION_SERVICE_URL:
                for name in face_names:
                    if name != "Unknown":  # Überprüfen, ob ein bekanntes Gesicht erkannt wurde
                        notify_service(name)

        process_this_frame = not process_this_frame
        if face_locations and face_names:
            for (top, right, bottom, left), name, landmarks in zip(face_locations, face_names, face_landmarks_list):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

            # Durchsichtige Box mit abgerundeten Ecken
            overlay = frame.copy()
            opacity = 0.25
            cv2.rectangle(overlay, (left, top), (right, bottom), (255, 220, 220), cv2.FILLED)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

            # Verbesserter Text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_width, text_height = cv2.getTextSize(name, font, 1, 2)[0]
            text_x = left + int((right - left) / 2) - int(text_width / 2)
            cv2.putText(frame, name, (text_x, bottom + text_height + 20), font, 1, (255, 255, 0), 2)

        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.route(OUTPUT_PATH)
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def guide():
    # Retrieve environment variables
    stream_url = os.getenv('INPUT_STREAM_URL')
    host_ip = os.getenv('OUTPUT_HOST')
    port = os.getenv('OUTPUT_PORT')
    video_path = os.getenv('OUTPUT_PATH')

    # Pass them to the template
    return render_template('index.html', stream_url=stream_url, host_ip=host_ip, port=port, video_path=video_path)


if __name__ == '__main__':
    app.run(host=OUTPUT_HOST, port=OUTPUT_PORT, threaded=True, use_reloader=False)
