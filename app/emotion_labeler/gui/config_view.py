import PySimpleGUI as gui
from const import VIEW_LOADING
from detectors import DETECTORS
from predictors import PREDICTORS
from undersamplers import UNDERSAMPLERS

from gui.framework import View
from gui.parameter_object import ParameterObject


class ConfigView(View):
    def __init__(self, key):
        super().__init__(key, size=(650, 440), visible=True)

        self.face_detectors = DETECTORS
        self.face_detector = None

        self.backends = PREDICTORS
        self.selected_backends = []

        self.undersamplers = UNDERSAMPLERS
        self.selected_undersampler = None

        self.current_file_path = None
        self.save_folder = None

    def build(self) -> list:
        return [
            [gui.Text('Config View', expand_x=True, font=('_', 16, 'bold'))],
            [gui.Sizer(h_pixels=400, v_pixels=8)],
            [
                gui.Text('Resource path'),
                gui.Push(),
                gui.Input(disabled=True, enable_events=True, key='InResource'),
                gui.FileBrowse(button_text='Choose', key='FileBrowse'),
                gui.Sizer(h_pixels=4)
            ],
            [gui.Sizer(v_pixels=8)],
            [
                gui.Text('Save folder'),
                gui.Push(),
                gui.Input(disabled=True, enable_events=True, key='InFolder'),
                gui.FolderBrowse(button_text='Choose', key='FolderBrowse'),
                gui.Sizer(h_pixels=4)
            ],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('Face Detector', font=('_', 14, 'bold'))],
            [gui.Checkbox(detector, enable_events=True, key=detector)
             for detector in self.face_detectors],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('Backend', font=('_', 14, 'bold'))],
            *[
                [
                    gui.Checkbox(backend, enable_events=True, key=backend),
                    gui.Push(),
                    gui.InputText(
                        '1.0',
                        key='Text{}'.format(backend),
                        disabled=True,
                        disabled_readonly_background_color='#aaaaaa',
                    ),
                    gui.Sizer(h_pixels=64)
                ]
                for backend in self.backends
            ],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('Undersampler', font=('_', 14, 'bold'))],
            *[
                [
                    gui.Checkbox(
                        undersampler,
                        enable_events=True,
                        key=undersampler
                    ),
                    gui.Push(),
                    gui.InputText(
                        '0.8',
                        key='Text{}'.format(undersampler),
                        disabled=True,
                        disabled_readonly_background_color='#aaaaaa',
                    ),
                    gui.Sizer(h_pixels=64)
                ]
                for undersampler in self.undersamplers],
            [gui.Sizer(v_pixels=24)],
            [
                gui.Button('Quit', key='ButtonQuit'),
                gui.Push(),
                gui.Button(
                    'Next',
                    key='ButtonNext',
                    disabled=True,
                    disabled_button_color='#aaaaaa'
                ),
                gui.Sizer(h_pixels=4),
            ],
        ]

    def handle_parameter_object(self, parameter_object):
        pass

    def is_next_disabled(self):
        return len(self.selected_backends) == 0 or self.face_detector == None or self.current_file_path == None or self.save_folder == None

    def safely_parse_float(self, number):
        try:
            return float(number)
        except:
            return 1.0

    def compute_undersampler(self):
        if self.selected_undersampler == None:
            return None
        return (
            self.selected_undersampler,
            self.safely_parse_float(
                self.window['Text{}'.format(self.selected_undersampler)].get()
            )
        )

    def handle_events(self, event, values):
        if event == 'InResource':
            self.current_file_path = values['InResource']
            self.window['ButtonNext'].update(disabled=self.is_next_disabled())

        elif event == 'InFolder':
            self.save_folder = values['InFolder']
            self.window['ButtonNext'].update(disabled=self.is_next_disabled())

        elif event in self.undersamplers:
            current_value = self.window[event].get()

            for undersampler in self.undersamplers:
                self.window[undersampler].update(False)
                self.window['Text{}'.format(undersampler)].update(disabled=True)

            self.window[event].update(current_value)
            self.window['Text{}'.format(event)].update(
                disabled=(not current_value))
            self.selected_undersampler = event if current_value else None

        elif event in self.face_detectors:
            current_value = self.window[event].get()

            for face_detector in self.face_detectors:
                self.window[face_detector].update(False)

            self.window[event].update(current_value)

            self.face_detector = event if current_value else None
            self.window['ButtonNext'].update(disabled=self.is_next_disabled())

        elif event in self.backends:
            if event in self.selected_backends:
                self.selected_backends.remove(event)
                self.window['Text{}'.format(event)].update(disabled=True)
            else:
                self.selected_backends.append(event)
                self.window['Text{}'.format(event)].update(disabled=False)

            self.window['ButtonNext'].update(disabled=self.is_next_disabled())

        elif event == 'ButtonNext':
            param_obj = ParameterObject(
                face_detector=self.face_detector,
                undersampler=self.compute_undersampler(),
                selected_backends={(b, self.safely_parse_float(self.window['Text{}'.format(b)].get()))
                                   for b in self.selected_backends},
                current_file_path=self.current_file_path,
                save_folder=self.save_folder,
            )
            self.change_view(VIEW_LOADING, param_obj)
