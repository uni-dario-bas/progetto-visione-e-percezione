from abc import ABC, abstractmethod

import cv2

import mediapipe as mp
mp_face_detection = mp.solutions.face_detection


DETECTORS = ['MediaPipe', 'Haar Cascades']


class Detector(ABC):
    @abstractmethod
    def detect(self, video) -> list:
        pass


class MediaPipeDetector(Detector):
    def process_image(self, image, face_detection) -> list:
        result = face_detection.process(image)

        if not result.detections:
            return []

        detections = []
        for detection in result.detections:

            relative_bounding_box = detection.location_data.relative_bounding_box

            if relative_bounding_box.ymin < 0 or relative_bounding_box.xmin < 0:
                return []

            y_min = int(image.shape[0] * relative_bounding_box.ymin)
            x_min = int(image.shape[1] * relative_bounding_box.xmin)
            y_max = int(
                image.shape[0] * (relative_bounding_box.ymin + relative_bounding_box.height))
            x_max = int(
                image.shape[1] * (relative_bounding_box.xmin + relative_bounding_box.width))

            cropped_img = image[y_min:y_max, x_min:x_max]

            scaled_img = cv2.resize(cropped_img, (48, 48))

            grayscaled_img = cv2.cvtColor(scaled_img, cv2.COLOR_RGB2GRAY)

            detections.append(grayscaled_img)

        return detections

    def detect(self, video) -> list:
        result = []

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            while video.isOpened():
                shouldContinue, image = video.read()

                if not shouldContinue:
                    break

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                result += self.process_image(image, face_detection)

        return result


class HaarCascadesDetector(Detector):
    def __init__(self, scale_factor=1.3, min_neighbors=5):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors

    def process_image(self, image):
        grayscaled_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        faces = self.face_cascade.detectMultiScale(
            grayscaled_img,
            self.scale_factor,
            self.min_neighbors
        )

        if len(faces) == 0:
            return []

        detections = []
        for face in faces:
            (x_min, y_min, width, height) = face

            cropped_img = grayscaled_img[
                y_min:(y_min + height),
                x_min:(x_min + width)
            ]

            detections.append(cv2.resize(cropped_img, (48, 48)))

        return detections

    def detect(self, video) -> list:
        result = []

        while video.isOpened():
            shouldContinue, image = video.read()

            if not shouldContinue:
                break

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result += self.process_image(image)

        return result


def create_detector(detector, scale_factor=1.3, min_neighbors=5) -> Detector:
    if detector == 'MediaPipe':
        return MediaPipeDetector()
    elif detector == 'Haar Cascades':
        return HaarCascadesDetector(scale_factor=scale_factor, min_neighbors=min_neighbors)
    else:
        raise Exception('Unknown detector: {}'.format(detector))
