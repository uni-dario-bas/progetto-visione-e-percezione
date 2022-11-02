import os

import cv2
import mediapipe as mp
import numpy as np
import PySimpleGUI as gui
from tensorflow.keras.models import load_model

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


# ---- Functions / State
def load_emoji(emoji_path):
    emoji = cv2.imread(os.path.join(
        current_path, emoji_path), cv2.IMREAD_UNCHANGED)
    emoji.flags.writeable = False
    emoji = cv2.cvtColor(emoji, cv2.COLOR_BGR2BGRA)
    return emoji


def process_image(img, face_detection):
    result = face_detection.process(img)

    if not result.detections:
        return -1, -1, -1, -1, np.empty([])

    detection = result.detections[0]

    relative_bounding_box = detection.location_data.relative_bounding_box

    if relative_bounding_box.ymin < 0 or relative_bounding_box.xmin < 0:
        return -1, -1, -1, -1, np.empty([])

    y_min = int(img.shape[0] * relative_bounding_box.ymin)
    x_min = int(img.shape[1] * relative_bounding_box.xmin)
    y_max = int(
        img.shape[0] * (relative_bounding_box.ymin + relative_bounding_box.height))
    x_max = int(
        img.shape[1] * (relative_bounding_box.xmin + relative_bounding_box.width))

    cropped_img = img[y_min:y_max, x_min:x_max]

    scaled_img = cv2.resize(cropped_img, (48, 48))

    grayscaled_img = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)

    return y_min, x_min, y_max, x_max, grayscaled_img


cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

current_path = os.path.dirname(__file__)

clf_vgg_like = load_model(os.path.join(
    current_path,
    'vgg-like-happy-sad',
))

classes = ['happy', 'sad']

classifiers = ['VGG Like']

happy_emoji = load_emoji('happy-emoji.png')
sad_emoji = load_emoji('sad-emoji.png')

# ---- View
layout = [
    [
        gui.Text('Classificatore: '),
        gui.Checkbox(classifiers[0], default=True,
                     key=classifiers[0], enable_events=True, disabled=True),
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
window = gui.Window('Emojis', layout=layout, font=('_', 14))

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while True:
        event, values = window.read(timeout=16)

        if event == gui.WINDOW_CLOSED:
            break

        if event in classifiers:
            for classifier in classifiers:
                window[classifier].update(False)
            window[event].update(True)
            currentClassifier = event

        _, img = cap.read()
        img.flags.writeable = False

        aabb_ymin, aabb_xmin, aabb_ymax, aabb_xmax, processed_image = process_image(
            img,
            face_detection
        )

        if processed_image.size == 1:
            window['-IMG-'].update(data=cv2.imencode('.png', img)[1].tobytes())
            continue

        prediction = np.argmax(clf_vgg_like.predict(
            np.reshape(processed_image, (-1, 48, 48, 1))
        ))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        emoji = happy_emoji if classes[prediction] == 'happy' else sad_emoji
        emoji = cv2.resize(
            emoji,
            (aabb_ymax - aabb_ymin, aabb_xmax - aabb_xmin)
        )

        y_min, y_max = aabb_ymin, aabb_ymin + emoji.shape[0]
        x_min, x_max = aabb_xmin, aabb_xmin + emoji.shape[1]
        if (y_max > img.shape[0] or x_max > img.shape[1]):
            window['-IMG-'].update(data=cv2.imencode('.png', img)[1].tobytes())
            continue

        alpha_emoji = emoji[:, :, 3] / 255.0
        alpha_img = 1.0 - alpha_emoji

        for c in range(0, 3):
            img[y_min:y_max, x_min:x_max, c] = (alpha_emoji * emoji[:, :, c] +
                                                alpha_img * img[y_min:y_max, x_min:x_max, c])

        window['-IMG-'].update(data=cv2.imencode('.png', img)[1].tobytes())

cap.release()
window.close()
