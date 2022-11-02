from random import shuffle
from abc import ABC, abstractmethod

import cv2


UNDERSAMPLERS = ['Random', 'Histogram']


class Undersampler(ABC):
    @abstractmethod
    def select(self, images) -> list:
        pass


class RandomUndersampler(Undersampler):
    def __init__(self, percentage=0.8):
        self.percentage = max(0.0, min(1.0, percentage))

    def select(self, images) -> list:
        shuffle(images)
        return images[0:int(len(images) * self.percentage)]


class HistogramUndersampler(Undersampler):
    def __init__(self, similarity=0.6):
        self.similarity = similarity

    def calculate_histogram(self, image):
        histogram = cv2.calcHist(
            image, [0], None,
            [256], [0, 256]
        )
        cv2.normalize(
            histogram, histogram,
            alpha=0, beta=1, norm_type=cv2.NORM_MINMAX
        )
        return histogram

    def select(self, images) -> list:
        result = []
        result.append(images[0])
        previous_histogram = self.calculate_histogram(images[0])

        for image in images[1:]:
            current_histogram = self.calculate_histogram(image)
            test = cv2.compareHist(previous_histogram, current_histogram, 0)

            if test < self.similarity:
                previous_histogram = current_histogram
                result.append(image)

        return result


def create_undersampler(undersampler, param=0.8) -> Undersampler:
    if undersampler == 'Random':
        return RandomUndersampler(percentage=param)
    elif undersampler == 'Histogram':
        return HistogramUndersampler(similarity=param)
    else:
        raise Exception('Unknown undersampler: {}'.format(undersampler))
