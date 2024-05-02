import os
import face_recognition
import numpy as np


class FaceLoader:
    def __init__(self):
        img_dir = os.path.join('data', 'knownfaces')
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces(img_dir)

    def load_known_faces(self, directory):
        try:
            for filename in os.listdir(directory):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(directory, filename)
                    image = face_recognition.load_image_file(file_path)
                    face_encodings = face_recognition.face_encodings(image)
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(os.path.splitext(filename)[0])
        except FileNotFoundError:
            print(f"Directory {directory} not found.")
        except Exception as e:
            print(f"Failed to load known faces: {e}")

    def get_name(self, face_encoding):
        distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
        if len(distances) > 0:  # Correct way to check if the distances array is not empty
            best_match_index = np.argmin(distances)
            if distances[best_match_index] < 0.5:  # Example threshold, adjust based on your accuracy needs
                return self.known_face_names[best_match_index]
        return "Unknown"