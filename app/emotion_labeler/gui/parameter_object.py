class ParameterObject:
    def __init__(
            self,
            face_detector=None,
            selected_backends=None,
            undersampler=None,
            current_file_path=None,
            save_folder=None,
            result=None,
            frames=None
    ):
        self.face_detector = face_detector
        self.selected_backends = selected_backends
        self.current_file_path = current_file_path
        self.save_folder = save_folder
        self.result = result
        self.undersampler = undersampler
        self.frames = frames
