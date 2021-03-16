from MaxSandbox.background_creator import (
    background_creator_model,
    background_creator_view,
    constants,
)
from MaxSandbox.shared_modules import message_box


class BackgroundCreatorController(object):
    """Controller of background_creator_gui.py and background_creator_model.py."""

    def __init__(self):
        self.model = None
        self.view = None
        self.camera_transform = None
        self.camera_shape = None
        self.manual_interface = None
        self.coi_vector = None
        self.current_cam_coordinates = None
        self.new_cam_position = None
        self.cam = None
        self.maximum_translation = None
        self._init_view()

    def _init_view(self):
        # initialize view class
        self.view = background_creator_view.main()

        # connect signals
        self.view.create_btn.clicked.connect(self.create_background_cam)
        self.view.get_selection_btn.clicked.connect(self._get_selected_cam)

    def _get_selected_cam(self):
        """Get selected camera. If no camera is selected, or more than 1 is selected, show an error message."""
        # initialize model class if it hasn't been initialized yet.
        if self.model is None:
            self.model = background_creator_model.BackgroundCreatorModel()

        # get selected camera. If returned value is None, create a 'selection error'-message box.
        self.camera_transform, self.camera_shape = self.model.fetch_selected_cam()
        if self.camera_transform is not None:
            self.view.camera_line_edit.setText(self.camera_transform)
        else:
            message_box.show_message(
                constants.NO_CAM_ERROR, self.view, constants.NO_CAM_MSG_TITLE
            )

    def create_background_cam(self):
        """Initialize model and create background camera."""
        if self.camera_transform is None:
            message_box.show_message(
                constants.NO_CAM_ERROR, self.view, constants.NO_CAM_MSG_TITLE
            )
            return

        if self.model is None:
            self.model = background_creator_model.BackgroundCreatorModel()

        (
            cam_translation,
            cam_translation_dict,
            aspect_ratio,
            resolution,
        ) = self.model.calculate_cam_translation(
            self.camera_shape, self.camera_transform
        )
        if resolution[0] == constants.MAXIMUM_RENDER_WIDTH:
            manual_mode = self.view.ask_manual_mode()
            if not manual_mode:
                _, _, new_cam_position, cam = self.model.init_background_cam(
                    cam_translation,
                    cam_translation_dict,
                    aspect_ratio,
                    resolution,
                    self.camera_transform,
                )
            else:
                # initialize background camera
                (
                    coi_vector,
                    current_cam_coordinates,
                    max_translate_position,
                    cam,
                ) = self.model.init_background_cam(
                    cam_translation,
                    cam_translation_dict,
                    aspect_ratio,
                    resolution,
                    self.camera_transform,
                )

                self.coi_vector = coi_vector
                self.current_cam_coordinates = current_cam_coordinates
                self.cam = cam
                self.maximum_translation = cam_translation

                # initialize manual interface
                self.manual_interface = background_creator_view.ManualInterface()
                self.manual_interface.show()
                self.manual_interface.translation_slider._slider.valueChanged.connect(
                    self.manual_translation
                )
        else:
            _, _, new_cam_position, cam = self.model.init_background_cam(
                cam_translation,
                cam_translation_dict,
                aspect_ratio,
                resolution,
                self.camera_transform,
            )

    def manual_translation(self):
        """Change camera translation based on user input."""
        percentage_slider_val = float(
            self.manual_interface.translation_slider._text.text()
        )
        user_translation = (
            self.maximum_translation / 100.0 * float(percentage_slider_val)
        )
        self.model.manually_translate_cam(
            user_translation, self.coi_vector, self.current_cam_coordinates, self.cam
        )


def main():
    """Initialize controller class."""
    controller = BackgroundCreatorController()
    return controller


if __name__ == "__main__":
    controller = main()
