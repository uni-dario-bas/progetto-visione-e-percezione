from abc import ABC, abstractmethod
import os

import numpy as np

from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Flatten, Dense, Dropout


PREDICTORS = ['VGG Like', 'DeepFace']


class Predictor(ABC):
    @abstractmethod
    def predict(self, images) -> list:
        pass


class VGGLikePredictor(Predictor):
    def __init__(self, weight=1.0):
        current_path = os.path.dirname(__file__)

        self.model = load_model(
            os.path.join(current_path, 'models/vgg-like')
        )

        self.weight = weight

    def predict(self, images) -> list:
        result = []

        reshaped_images = np.reshape(images, (-1, 48, 48, 1))
        predictions = self.model.predict(reshaped_images)

        for prediction in predictions:
            result.append([p * self.weight for p in prediction])

        return result


class DeepFacePredictor(Predictor):
    def __init__(self, emotion_labels, weight=1.0):
        self.model_emotion_labels = [
            'angry', 'disgust', 'fear',
            'happy', 'sad', 'surprise', 'neutral'
        ]

        self.emotion_labels = emotion_labels

        num_classes = len(self.model_emotion_labels)

        self.model = Sequential()

        # 1st convolution layer
        self.model.add(
            Conv2D(64, (5, 5), activation='relu', input_shape=(48, 48, 1)))
        self.model.add(MaxPooling2D(pool_size=(5, 5), strides=(2, 2)))

        # 2nd convolution layer
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(Conv2D(64, (3, 3), activation='relu'))
        self.model.add(AveragePooling2D(pool_size=(3, 3), strides=(2, 2)))

        # 3rd convolution layer
        self.model.add(Conv2D(128, (3, 3), activation='relu'))
        self.model.add(Conv2D(128, (3, 3), activation='relu'))
        self.model.add(AveragePooling2D(pool_size=(3, 3), strides=(2, 2)))

        self.model.add(Flatten())

        # fully connected neural networks
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dropout(0.2))

        self.model.add(Dense(num_classes, activation='softmax'))

        current_path = os.path.dirname(__file__)
        current_path = os.path.join(
            current_path,
            'models/facial_expression_model_weights.h5'
        )

        self.model.load_weights(current_path)

        self.weight = weight

    def sort_prediction(self, prediction) -> list:
        ordered_predictions = [
            None for _ in range(len(self.model_emotion_labels))
        ]

        for index, emotion in enumerate(self.model_emotion_labels):
            ordered_index = self.emotion_labels.index(emotion)
            ordered_predictions[ordered_index] = prediction[index]

        return ordered_predictions

    def predict(self, images) -> list:
        result = []

        reshaped_images = np.reshape(images, (-1, 48, 48, 1))
        predictions = self.model.predict(reshaped_images)

        for prediction in predictions:
            sorted_prediction = self.sort_prediction(
                [p * self.weight for p in prediction]
            )
            result.append(sorted_prediction)

        return result


def create_predictor(predictor, emotion_labels, weight=1.0) -> Predictor:
    if predictor == 'VGG Like':
        return VGGLikePredictor(weight=weight)
    elif predictor == 'DeepFace':
        return DeepFacePredictor(emotion_labels=emotion_labels, weight=weight)
    else:
        raise Exception('Unknown predictor: {}'.format(predictor))
