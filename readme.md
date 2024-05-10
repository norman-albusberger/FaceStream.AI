# Face Recognition Streaming Service

## Project Description
This project is a Dockerized face recognition application that processes video streams to identify known faces. It uses the `face_recognition` library for recognizing faces in video frames and Flask to stream the processed video over HTTP.


## Introduction
This service offers a real-time face recognition feature, deploying two main components: the ConfigServer for configuration management and the 
VideoStreamServer for face recognition service and streaming of a mjpeg video with the recognized faces marked by rectangle.

## Features
- Real-time video streaming with face recognition.
- Configurable settings via a web interface on the ConfigServer.
- Easy management of known faces for recognition.
- HTTP & UDP messaging if face is recognized
- Face recognition service does not depend on streaming (anymore). 

## Technologies
- Flask for creating web interfaces.
- Docker for containerizing and managing application components.
- Python for backend

## Installation
1. Clone this repository to your local machine.
2. Ensure Docker and Docker Compose are installed.
3. Navigate to the cloned directory and run `docker-compose up`.

## Usage
- Access the ConfigServer web interface to configure streaming settings. 
- Stream live video with face recognition from the VideoStreamServer.

Access the ConfigServer web interface at http://<DOCKER_HOST>:<CONFIGSERVER_PORT> to configure streaming parameters.
View the live video stream at http://<DOCKER_HOST>:<VIDEOSTREAM_PORT>.

## Container Run Options

```-p 8000:5000 -p 8080:5001 -v data:/FaceStream.ai/data``` 

#### Port Mapping
- **Port 8000 (Host) -> Port 5000 (Container)**:
  - This port is mapped to the default port used by the application for serving the configuration web service.

- **Port 8080 (Host) -> Port 5001 (Container)**:
  - This port is mapped to the default port used by the video service.

#### Volume Mounting
- **data:/FaceStream.ai/data**:
  - This volume is mounted to store persistent data used by the application. It allows the application to store and access data such as the config.json and knownfaces folder.


## Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
