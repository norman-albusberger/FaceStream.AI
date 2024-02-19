import os
import face_recognition
import cv2
import numpy as np
from flask import Flask, Response

# Configuration from environment variables
INPUT_STREAM_URL = os.getenv('INPUT_STREAM_URL', '/dev/video0')
OUTPUT_HOST = os.getenv('OUTPUT_HOST', '0.0.0.0')
OUTPUT_PORT = int(os.getenv('OUTPUT_PORT', '5000'))
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/video_feed')

app = Flask(__name__)




def generate_frames():
    video_capture = cv2.VideoCapture(INPUT_STREAM_URL)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Existing face recognition logic here...

        # Encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue

        # Yield the frame
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route(OUTPUT_PATH)
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host=OUTPUT_HOST, port=OUTPUT_PORT, threaded=True, use_reloader=False)
