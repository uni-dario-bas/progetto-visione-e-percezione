import os
from pathlib import Path

import cv2
import PySimpleGUI as gui
from const import VIEW_CONFIG

from gui.framework import View
from gui.parameter_object import ParameterObject


class SaveView(View):
    def build(self) -> list:
        return [
            [gui.Text('Saving', expand_x=True, font=('_', 16, 'bold'))],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('', key='TextCurrentFrame')],
        ]

    def handle_parameter_object(self, parameter_object: ParameterObject):
        for index, frame in enumerate(parameter_object.frames):
            self.window['TextCurrentFrame'].update(
                'Saving image {} of {}'.format(
                    index + 1, len(parameter_object.frames)
                )
            )
            self.window.refresh()
            path = os.path.join(parameter_object.save_folder, frame[1])
            Path(path).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(
                os.path.join(path, '{}.jpg'.format(index)),
                frame[0],
            )

        self.change_view(VIEW_CONFIG)

    def handle_events(self, event, values):
        pass
