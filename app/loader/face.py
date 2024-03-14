import os
from config.manager import ConfigManager
import face_recognition


class FaceLoader:
    def __init__(self):
        config_path = os.path.join('data', 'config.json')
        self.config_manager = ConfigManager(config_path)
        image_directory = self.config_manager.get('image_directory')
        print("test")
        print(image_directory)
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces(image_directory)

    def load_known_faces(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(directory, filename)
                image = face_recognition.load_image_file(file_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])
