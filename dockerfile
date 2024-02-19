# Use an official lightweight Python image as the base image
FROM python:3.8-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Install system dependencies required for the face_recognition and OpenCV libraries
# Combine apt-get update, package installation, and cleanup into a single RUN command to reduce image layers and size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Use pip to install the face_recognition library directly from the repository to get the latest version
# Install opencv-python-headless to avoid unnecessary GUI dependencies for headless environments
RUN pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition \
    && pip install --no-cache-dir opencv-python-headless \
    && pip install flask

# ENV INPUT_STREAM_URL sets the default URL for the input video stream.
# Replace "http://example.com/stream" with the actual stream URL when starting the container using -e option.
ENV INPUT_STREAM_URL="http://example.com/stream"

# ENV OUTPUT_HOST configures the host IP for the output stream.
# "0.0.0.0" makes the Flask server accessible on all network interfaces of the container.
ENV OUTPUT_HOST="0.0.0.0"

# ENV OUTPUT_PORT sets the port number on which the Flask server will listen for incoming connections.
# 5000 is a commonly used default port for web applications.
ENV OUTPUT_PORT=5000

# ENV OUTPUT_PATH specifies the URL path where the output video stream can be accessed.
# For example, setting it to "/video" means the stream will be available at http://<container-ip>:5000/video
ENV OUTPUT_PATH="/video"

# Set the default command to execute the face recognition script when the container starts
CMD ["python", "./face-recognition-stream.py"]
