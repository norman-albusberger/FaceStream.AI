import threading
import logging
import cv2
import face_recognition
import queue
import time


class FrameProcessor(threading.Thread):
    def __init__(self, frame_queue, processed_frame_queue, face_loader, config_manager, notification_service):
        super().__init__()
        self.frame_queue = frame_queue
        self.processed_frame_queue = processed_frame_queue
        self.config_manager = config_manager
        config_manager.load_config()
        self.overlay_transparency = config_manager.get('overlay_transparency')
        self.overlay_color = config_manager.get('overlay_color')
        self.face_recognition_interval = config_manager.get('face_recognition_interval')
        self.face_loader = face_loader
        self.running = True
        self.trackers = []
        self.notification_service = notification_service
        self.frame_count = 0  # Zähler für die Frame-Intervalle
        self.scale_factor = 0.5

    def run(self):
        while self.running:
            try:
                frame = self.frame_queue.get()
                if frame is not None:
                    if self.frame_count % self.face_recognition_interval == 0:
                        processed_frame = self.process_frame(frame)
                    else:
                        processed_frame = self.update_trackers(frame)  # Aktualisiere immer die Tracker

                    try:
                        self.processed_frame_queue.put_nowait(processed_frame)
                    except queue.Full:
                        # Leere die Queue, wenn sie voll ist
                        while not self.processed_frame_queue.empty():
                            try:
                                self.processed_frame_queue.get_nowait()
                            except queue.Empty:
                                break
                        logging.debug("Processed frame queue was full and has been cleared.")
                        self.processed_frame_queue.put_nowait(
                            processed_frame)  # Versuche, den aktuellen Frame erneut hinzuzufügen

                self.frame_count += 1
                if self.frame_count % 100 == 0:
                    queue_size = self.frame_queue.qsize()
                    logging.debug(f"Aktuelle Queue-Größe: {queue_size}; verarbeitete Frames: {self.frame_count}")

                # Zurücksetzen des frame_count, um Überlauf zu vermeiden
                if self.frame_count >= 1000000:
                    self.frame_count = 0

            except queue.Empty:
                continue

    def stop(self):
        self.running = False

    def process_frame(self, frame):
        start_time = time.time()
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        # Convert small frame to RGB from BGR, which OpenCV uses
        rgb_small_frame = small_frame[:, :, ::-1]

        # Reset trackers on new detection
        self.trackers = []

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Create a copy of the original frame to draw on
        marked_frame = frame.copy()

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = self.face_loader.get_name(face_encoding)
            # Initialize a new tracker for each face
            tracker = cv2.TrackerKCF_create()
            # Convert face location from small frame scale to original scale
            # Skalierung zurücksetzen
            scale_multiplier = int(1 / self.scale_factor)
            top, right, bottom, left = (top * scale_multiplier,
                                        right * scale_multiplier,
                                        bottom * scale_multiplier,
                                        left * scale_multiplier)
            bbox = (left, top, right - left, bottom - top)
            tracker.init(frame, bbox)
            self.trackers.append({'tracker': tracker, 'name': name})

            # Draw rectangles and notify
            name = self.face_loader.get_name(face_encoding)  # Assuming a method to get name
            marked_frame = self.draw_rectangle_with_name(marked_frame, top, right, bottom, left, name)
            self.notification_service.notify(name, marked_frame)

            processing_time = time.time() - start_time
            logging.debug(f"Frame verarbeitet in {processing_time:.2f} Sekunden")

        return frame

    def update_trackers(self, frame):
        new_trackers = []
        updated_frame = frame.copy()  # Erstelle eine Kopie für Updates
        for tracked in self.trackers:
            tracker = tracked['tracker']
            name = tracked['name']
            success, box = tracker.update(updated_frame)
            if success:
                left, top, width, height = [int(v) for v in box]
                right, bottom = left + width, top + height
                updated_frame = self.draw_rectangle_with_name(updated_frame, top, right, bottom, left, name)
                new_trackers.append(tracked)
            else:
                logging.debug(f"Tracking failed for {name}, removing tracker.")
        self.trackers = new_trackers
        return updated_frame

    def draw_rectangle_with_name(self, frame, top, right, bottom, left, name):
        try:
            border_color = (255, 255, 255)  # Weiß
            border_thickness = 1  # Stärke der weißen Border
            rectangle_thickness = -1  # Füllt das Rechteck
            transparency = self.overlay_transparency
            overlay_color = self.overlay_color[::-1]
            overlay = frame.copy()
            cv2.rectangle(overlay, (left, top), (right, bottom), overlay_color, rectangle_thickness)
            # Hier wird die Schriftgröße angepasst
            font_scale = 1.0  # Erhöhe diesen Wert, um die Schriftgröße zu vergrößern
            font_thickness = 2  # die Schriftstärke anpassen, falls nötig
            cv2.rectangle(frame, (left - border_thickness, top - border_thickness),
                          (right + border_thickness, bottom + border_thickness), border_color, border_thickness)
            blended_frame = cv2.addWeighted(overlay, 1 - transparency, frame, transparency, 0)
            cv2.putText(blended_frame, name, (left, bottom + border_thickness + 25), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (255, 255, 255),
                        font_thickness)
        except Exception as e:
            logging.debug(f"Failed to draw rectangle with name: {e}")
            return frame  # Rückgabe des ursprünglichen Frames im Fehlerfall
        return blended_frame
