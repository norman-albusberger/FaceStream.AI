import os
import face_recognition
import cv2
import numpy as np
from flask import Flask, Response, render_template

# Configuration from environment variables
INPUT_STREAM_URL = os.getenv('INPUT_STREAM_URL', '/dev/video0')
OUTPUT_HOST = os.getenv('OUTPUT_HOST', '0.0.0.0')
OUTPUT_PORT = int(os.getenv('OUTPUT_PORT', '5000'))
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/video')
IMAGE_DIRECTORY = os.getenv('IMAGE_DIRECTORY', '/default/path/if/not/set')

app = Flask(__name__)

# Lists to store known face encodings and names
known_face_encodings = []
known_face_names = []

# Iterate through all files in the directory
imageDir = os.listdir(IMAGE_DIRECTORY)
for filename in imageDir:
    print(filename)

    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):  # Check if the file is an image
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


def generate_frames():
    video_capture = cv2.VideoCapture(INPUT_STREAM_URL)
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()

        if not ret:
            break

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        process_this_frame = not process_this_frame

        # Encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue

        # Yield the frame
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
