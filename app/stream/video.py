import cv2
import time
import face_recognition


class VideoStream:
    def __init__(self, face_loader, config_manager, notification_service):
        self.config_manager = config_manager
        config_manager.load_config()
        self.video_capture = cv2.VideoCapture(config_manager.get('input_stream_url'))
        self.overlay_transparency = config_manager.get('overlay_transparency')
        self.overlay_color = config_manager.get('overlay_color')
        print(self.overlay_color)
        self.output_width = config_manager.get('output_width')
        self.output_height = config_manager.get('output_height')
        self.face_loader = face_loader

        self.notification_service = notification_service
        self.face_recognition_interval = config_manager.get('face_recognition_interval')
        self.trackers = []  # Initialize a list to hold trackers

    def update_trackers(self, frame):
        for tracked in self.trackers:
            tracker = tracked['tracker']
            name = tracked['name']
            success, box = tracker.update(frame)
            if success:
                left, top, width, height = [int(v) for v in box]
                right, bottom = left + width, top + height
                self.draw_rectangle_with_name(frame, top, right, bottom, left, name)

    def draw_rectangle_with_name(self, frame, top, right, bottom, left, name):
        try:
            transparency = self.overlay_transparency
            overlay = frame.copy()
            cv2.rectangle(overlay, (left, top), (right, bottom), self.overlay_color, -1)  # Fills the rectangle

            # Safely attempt to blend the overlay with the original frame
            blended_frame = cv2.addWeighted(overlay, transparency, frame, 1 - transparency, 0)

            # Apply the blended frame back to the original frame reference
            frame[:, :] = blended_frame
            cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        except Exception as e:
            print(f"Failed to draw rectangle with name: {e}")

    def process_frame(self, small_frame, original_frame):
        # Convert small frame to RGB from BGR, which OpenCV uses
        rgb_small_frame = small_frame[:, :, ::-1]

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Reset trackers on new detection
        self.trackers = []
        # Process each face found
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = self.face_loader.get_name(face_encoding)
            # Initialize a new tracker for each face
            tracker = cv2.TrackerKCF_create()
            # Convert face location from small frame scale to original scale
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
            bbox = (left, top, right - left, bottom - top)
            tracker.init(original_frame, bbox)
            self.trackers.append({'tracker': tracker, 'name': name})

            # Draw rectangles and notify
            name = self.face_loader.get_name(face_encoding)  # Assuming a method to get name
            self.notification_service.notify(name)
            self.draw_rectangle_with_name(original_frame, top, right, bottom, left, name)

    def generate_frames(self):
        frame_counter = 0

        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                continue  # Handle failed frame read

            frame = cv2.resize(frame, (self.output_width, self.output_height))

            # Run face detection at intervals
            if frame_counter % self.face_recognition_interval == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                self.process_frame(small_frame, frame)
            else:
                # Update tracking on other frames
                self.update_trackers(frame)

            frame_counter += 1

            # Encode the processed frame into JPEG for streaming
            flag, encodedImage = cv2.imencode(".jpg", frame)
            if not flag:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
