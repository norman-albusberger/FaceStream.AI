# Face Recognition Streaming App

## Project Description
This project is a Dockerized face recognition application that processes video streams to identify known faces. It uses the `face_recognition` library for recognizing faces in video frames and Flask to stream the processed video over HTTP. The application is designed to be flexible, allowing for easy customization of input streams, known faces, and streaming endpoints through environment variables.

## Prerequisites
- Docker
- Docker Compose (optional, for easier management of Docker containers)

## Setup Instructions

### 1. Clone the Repository
Clone this repository to your local machine to get started.
```
git clone <repository-url>
cd <repository-directory>
```

### 2. Prepare Image Directory
Place images of known individuals in the `knownfaces` directory, with the file name as the identifier for the face (e.g., `john_doe.jpg` for John Doe).

### 3. Configure Environment Variables
Create a `.env` file in the root directory of the project and define the necessary environment variables:
```plaintext
INPUT_STREAM_URL=<your_input_stream_url>
OUTPUT_HOST=0.0.0.0
OUTPUT_PORT=5000
OUTPUT_PATH=/video
IMAGE_DIRECTORY=/app/test-images
```
Replace `<your_input_stream_url>` with the actual stream URL of your video source.

### 4. Build and Run the Docker Container
Using Docker Compose:
```
docker-compose up --build
```
Or using Docker:
```
docker build -t face-recognition-app .
docker run -p 8080:8080 --env-file .env face-recognition-app
```

## Usage
After starting the application, access the processed video stream by navigating to `http://localhost:8080/video` in your web browser, where `8080` is the host port you've mapped to the container's port `8080`.

## Customization
- **Input Stream**: Change the `INPUT_STREAM_URL` in the `.env` file to use a different video source.
- **Known Faces**: Add or remove images in the `knownfaces` directory to update the list of known individuals.
- **Streaming Endpoint**: Modify `OUTPUT_PATH` to change the URL endpoint for the video stream.

## Troubleshooting
- Ensure that the input stream URL is correct and accessible from within the Docker container.
- Verify that the `knownfaces` directory contains properly named image files of known faces.
- Check Docker logs for any errors or issues during the container startup or runtime.

For more information and detailed troubleshooting, refer to the official documentation of the `face_recognition` and Flask libraries.
