import cv2
import PySimpleGUI as gui
from const import EMOTIONS, VIEW_CONFIG, VIEW_SAVE

from gui.framework import View
from gui.parameter_object import ParameterObject


class LabelView(View):
    def __init__(self, key):
        super().__init__(key)

        self.save_folder = None
        self.frames = None
        self.emotions = EMOTIONS
        self.current_frame = 0

    def build(self) -> list:
        return [
            [gui.Text('Labeler', expand_x=True, font=('_', 16, 'bold'))],
            [gui.Sizer(v_pixels=8)],
            [gui.Text('', key='TextCurrentImage')],
            [gui.Sizer(v_pixels=8)],
            [
                gui.Push(),
                gui.Image(key='ImageCurrent'),
                gui.Text('Current image is labeled as: '),
                gui.Combo(self.emotions, size=(30, 22), enable_events=True,
                          readonly=True, key='ComboEmotions'),
                gui.Sizer(h_pixels=100),
            ],
            [gui.Sizer(v_pixels=8)],
            [
                gui.Button('Menu', key='ButtonMenu'),
                gui.Push(),
                gui.Button('Previous', key='ButtonPreviousFrame',
                           disabled=True, disabled_button_color='#aaaaaa'),
                gui.Sizer(h_pixels=4),
                gui.Button(
                    'Discard',
                    key='ButtonDiscard',
                    button_color='#ff0000',
                    disabled_button_color='#aaaaaa'
                ),
                gui.Sizer(h_pixels=4),
                gui.Button('Next', key='ButtonNextFrame'),
                gui.Sizer(h_pixels=100),
            ],
        ]

    def show_current_frame(self):
        self.window['TextCurrentImage'].update(
            'Image {} of {}'.format(self.current_frame + 1, len(self.frames))
        )
        self.window['ImageCurrent'].update(
            data=cv2.imencode(
                '.png',
                self.frames[self.current_frame][0]
            )[1].tobytes()
        )
        self.window['ComboEmotions'].update(
            self.frames[self.current_frame][1]
        )

    def handle_parameter_object(self, parameter_object: ParameterObject):
        self.frames = [[image, emotion_label]
                       for image, emotion_label in parameter_object.result]
        self.save_folder = parameter_object.save_folder
        self.current_frame = 0
        self.window.refresh()
        self.show_current_frame()
        self.window.refresh()

    def reset(self):
        self.window['ButtonNextFrame'].update('Next')
        self.frames = None
        self.current_frame = 0
        self.save_folder = None

    def save_and_reset(self):
        frames = self.frames
        save_folder = self.save_folder
        self.reset()
        self.change_view(
            VIEW_SAVE,
            ParameterObject(frames=frames, save_folder=save_folder),
        )

    def handle_events(self, event, values):
        if event == 'ButtonMenu':
            self.reset()
            self.change_view(VIEW_CONFIG)

        elif event == 'ComboEmotions':
            self.frames[self.current_frame][1] = values['ComboEmotions']

        elif event == 'ButtonDiscard':
            if len(self.frames) == 1:
                return

            del self.frames[self.current_frame]

            if self.current_frame > len(self.frames) - 1:
                self.current_frame -= 1

            if self.current_frame == len(self.frames) - 1:
                self.window['ButtonNextFrame'].update('Save')

            self.show_current_frame()

            if len(self.frames) == 1:
                self.window['ButtonDiscard'].update(disabled=True)
                self.window['ButtonPreviousFrame'].update(disabled=True)
                self.window['ButtonNextFrame'].update('Save')

        elif event == 'ButtonNextFrame':
            if self.current_frame == len(self.frames) - 1:
                self.save_and_reset()
                return

            self.current_frame += 1
            self.show_current_frame()
            if self.current_frame == len(self.frames) - 1:
                self.window['ButtonNextFrame'].update('Save')
            self.window['ButtonPreviousFrame'].update(disabled=False)

        elif event == 'ButtonPreviousFrame':
            if self.current_frame == 0:
                return

            self.current_frame -= 1
            self.show_current_frame()
            if self.current_frame == 0:
                self.window['ButtonPreviousFrame'].update(disabled=True)
            self.window['ButtonNextFrame'].update('Next')
