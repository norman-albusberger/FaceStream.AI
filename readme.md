# Face Recognition Streaming Service

## Project Description
This project is a Dockerized face recognition application that processes video streams to identify known faces. It uses the `face_recognition` library for recognizing faces in video frames and Flask to stream the processed video over HTTP.


## Introduction
This service offers a real-time face recognition feature, deploying two main components: the ConfigServer for configuration management and the VideoStreamServer for live video streaming with face recognition capabilities.

## Features
- Real-time video streaming with face recognition.
- Configurable settings via a web interface on the ConfigServer.
- Easy management of known faces for recognition.

## Technologies
- Flask for creating web interfaces.
- Docker for containerizing and managing application components.
- Python for backend development.

## Installation
1. Clone this repository to your local machine.
2. Ensure Docker and Docker Compose are installed.
3. Navigate to the cloned directory and run `docker-compose up`.

## Usage
- Access the ConfigServer web interface to configure streaming settings.
- Stream live video with face recognition from the VideoStreamServer.

Access the ConfigServer web interface at http://<DOCKER_HOST>:<CONFIGSERVER_PORT> to configure streaming parameters.
View the live video stream at http://<DOCKER_HOST>:<VIDEOSTREAM_PORT>.

## Configuration
Edit the `.env` file to customize the host ports and other settings as needed.

## Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
