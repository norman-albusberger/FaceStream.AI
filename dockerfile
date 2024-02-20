# Use an official lightweight Python image as the base image
FROM python:3.8-slim

# Set the working directory inside the container to /app
WORKDIR /app

# for local
#COPY app /app

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

# Set the default command to execute the face recognition script when the container starts
CMD ["python", "face-recognition-stream.py"]
