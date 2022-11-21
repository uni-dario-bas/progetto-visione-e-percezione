import os
import sys

import cv2
import numpy as np
import PySimpleGUI as gui
from tensorflow.keras.models import load_model

import mediapipe as mp
mp_face_detection = mp.solutions.face_detection


# ---- Functions / State
def process_image(face_detection, image):
    result = face_detection.process(image)

    if not result.detections:
        return [], []

    detections = []
    aabbs = []

    for detection in result.detections:

        relative_bounding_box = detection.location_data.relative_bounding_box

        if relative_bounding_box.ymin < 0 or relative_bounding_box.xmin < 0:
            return [], []

        y_min = int(image.shape[0] * relative_bounding_box.ymin)
        x_min = int(image.shape[1] * relative_bounding_box.xmin)
        y_max = int(
            image.shape[0] * (relative_bounding_box.ymin + relative_bounding_box.height))
        x_max = int(
            image.shape[1] * (relative_bounding_box.xmin + relative_bounding_box.width))
        aabbs.append(((x_min, y_min), (x_max, y_max)))

        cropped_img = image[y_min:y_max, x_min:x_max]

        scaled_img = cv2.resize(cropped_img, (48, 48))

        grayscaled_img = cv2.cvtColor(scaled_img, cv2.COLOR_RGB2GRAY)

        detections.append(grayscaled_img)

    return aabbs, detections


WHITE = (255, 255, 255)
EMOTIONS = ['happy', 'sad', 'angry', 'disgust', 'fear', 'neutral', 'surprise']

current_path = os.path.dirname(__file__)

clf_vgg_like = load_model(os.path.join(
    current_path,
    'vgg-like',
))

layout = [
    [
        gui.Text('Classificatore: '),
        gui.Checkbox('VGG-16 Like', default=True,
                     key='VGG-16 Like', enable_events=True, disabled=True),
    ],
    [gui.Sizer(v_pixels=8)],
    [
        gui.Text('Face Detector: '),
        gui.Checkbox('Mediapipe', default=True, disabled=True),
    ],
    [gui.Sizer(v_pixels=16)],
    [gui.Image(key='-IMG-')],
]

# ---- App
if (len(sys.argv) < 2):
    raise Exception('The file path must be specified!')

file_path = sys.argv[1]
model_selection = 1 if len(sys.argv) == 2 or sys.argv[2] == '1' else 0
video = cv2.VideoCapture(file_path)
if not video.isOpened():
    raise Exception('Cannot open file {}'.format(file_path))

window = gui.Window('Video Detection', layout=layout, font=('_', 14))

with mp_face_detection.FaceDetection(model_selection=model_selection, min_detection_confidence=0.5) as detector:
    while video.isOpened():
        shouldContinue, image = video.read()

        if not shouldContinue:
            break

        event, values = window.read(timeout=16)
        if event == gui.WINDOW_CLOSED:
            break

        image.flags.writeable = False
        faces, detections = process_image(detector, image)

        if (len(faces) == 0):
            window['-IMG-'].update(
                data=cv2.imencode('.png', image)[1].tobytes()
            )
            continue

        for result in zip(faces, detections):
            start_point, end_point = result[0]
            image = cv2.rectangle(
                image, start_point, end_point, WHITE, 1
            )

            reshaped_image = np.reshape(result[1], (-1, 48, 48, 1))
            predictions = clf_vgg_like.predict(reshaped_image)
            emotion_index = np.argmax(predictions)
            image = cv2.putText(
                image, EMOTIONS[emotion_index], (start_point[0], start_point[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2
            )

        window['-IMG-'].update(data=cv2.imencode('.png', image)[1].tobytes())

window.close()
