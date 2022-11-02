import cv2
import numpy as np
import PySimpleGUI as gui
from const import EMOTIONS, VIEW_LABEL
from detectors import create_detector
from predictors import create_predictor
from undersamplers import create_undersampler

from gui.framework import View
from gui.parameter_object import ParameterObject


class LoadingView(View):
    def __init__(self, key):
        super().__init__(key)

    def build(self) -> list:
        return [
            [gui.Text('Loading...', expand_x=True, font=('_', 16, 'bold'))],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('', key='TextStatus')]
        ]

    def handle_parameter_object(self, parameter_object: ParameterObject):
        self.window['TextStatus'].update('Opening video')
        self.window.refresh()
        video = cv2.VideoCapture(parameter_object.current_file_path)
        if not video.isOpened():
            raise Exception('Cannot open file {}'.format(
                parameter_object.current_file_path
            ))

        self.window['TextStatus'].update('Processing video')
        self.window.refresh()

        images = create_detector(parameter_object.face_detector) \
            .detect(video)

        if parameter_object.undersampler != None:
            undersampler, param = parameter_object.undersampler
            images = create_undersampler(undersampler, param).select(images)

        predictions = [[0 for _ in EMOTIONS] for _ in images]

        for (backend, weight) in parameter_object.selected_backends:
            self.window['TextStatus'].update(
                'Making predictions using {} (weight = {})'.format(
                    backend,
                    weight
                )
            )
            self.window.refresh()
            result = create_predictor(backend, emotion_labels=EMOTIONS, weight=weight) \
                .predict(images)
            predictions = np.add(result, predictions)

        emotion_indices = np.argmax(predictions, axis=1)
        emotions = [EMOTIONS[index] for index in emotion_indices]
        result = zip(images, emotions)

        self.change_view(
            VIEW_LABEL,
            parameter_object=ParameterObject(
                result=result,
                save_folder=parameter_object.save_folder,
            ),
        )

    def handle_events(self, event, values):
        pass
