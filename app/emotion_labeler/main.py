import PySimpleGUI as gui

from const import VIEW_CONFIG, VIEW_LABEL, VIEW_LOADING, VIEW_SAVE
from gui.config_view import ConfigView
from gui.label_view import LabelView
from gui.loading_view import LoadingView
from gui.save_view import SaveView


def main():
    views = {
        VIEW_CONFIG: ConfigView(VIEW_CONFIG),
        VIEW_LOADING: LoadingView(VIEW_LOADING),
        VIEW_LABEL: LabelView(VIEW_LABEL),
        VIEW_SAVE: SaveView(VIEW_SAVE),
    }

    layout = [[
        view.create() for view in views.values()
    ]]

    window = gui.Window('How are You?', layout=layout, font=('_', 14))

    for view in views.values():
        view.set_window_and_views(window, views)

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED or event == 'ButtonQuit':
            break

        for view in views.values():
            view.process(event, values)


if __name__ == '__main__':
    main()
