import os
from config.manager import ConfigManager
import face_recognition


class FaceLoader:
    def __init__(self):
        img_dir = os.path.join('/data', 'knownfaces')
        print("test")
        print(img_dir)
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces(img_dir)

    def load_known_faces(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(directory, filename)
                image = face_recognition.load_image_file(file_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])
