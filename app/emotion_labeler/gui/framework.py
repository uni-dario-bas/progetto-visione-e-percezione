from abc import ABC, abstractmethod

import PySimpleGUI as gui


class View(ABC):
    def __init__(self, key, size=(650, None), visible=False):
        self.window = None
        self.views = None
        self.key = key
        self.size = size
        self.visible = visible

    def set_window_and_views(self, window, views):
        self.window = window
        self.views = views

    def change_view(self, key, parameter_object=None):
        self.window[self.key].update(visible=False)
        self.window[key].update(visible=True)

        if parameter_object != None:
            self.views[key].handle_parameter_object(parameter_object)

    def create(self):
        return gui.Column(
            layout=self.build(),
            key=self.key,
            size=self.size,
            visible=self.visible,
            expand_x=True,
            expand_y=True
        )

    @abstractmethod
    def build(self) -> list:
        pass

    @abstractmethod
    def handle_parameter_object(self, parameter_object):
        pass

    def process(self, event, values):
        if not self.window[self.key].visible:
            return

        self.handle_events(event, values)

    @abstractmethod
    def handle_events(self, event, values):
        pass
