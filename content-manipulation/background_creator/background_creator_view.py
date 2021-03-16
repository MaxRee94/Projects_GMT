from CyBase.cute.widgets import CyMayaWidget, FloatSliderWidget
from MaxSandbox.background_creator import constants
from MaxSandbox.shared_modules import message_box, style_sheet
from Qt import QtCore, QtWidgets


class BackgroundCreatorView(CyMayaWidget):
    """Create an interface window for the background creator tool."""

    OBJECT_NAME = "BackgroundCreatorView"
    WINDOW_TITLE = "Background Cam Creator v1.0"
    CAM_LABEL_TXT = "Camera:"
    GET_CAM_TXT = "Get Selected"
    CREATE_BTN_TXT = "Create Background Camera"

    def __init__(self, center=True, parent=None):
        """Initialize class."""
        super(BackgroundCreatorView, self).__init__(center=center, parent=parent)
        self.default_camera = None
        self.create_btn = None
        self.get_selection_btn = None
        self.camera_line_edit = None

        self._init_main_layout()

    def _get_object_name(self):
        return self.OBJECT_NAME

    def _get_window_title(self):
        return self.WINDOW_TITLE

    def _init_main_layout(self):
        self.resize(350, 80)
        self.setMinimumWidth(350)
        self.setMaximumWidth(600)
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setStyleSheet(style_sheet.sheet)

        self.main_layout = QtWidgets.QGridLayout(self)
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(2, 2, 2, 2)

        cam_layout = self._create_cam_layout()
        self.main_layout.addLayout(cam_layout, 0, 0)

        spacing = QtWidgets.QLabel("")
        self.main_layout.addWidget(spacing)

        self.create_btn = QtWidgets.QPushButton(self.CREATE_BTN_TXT)
        self.main_layout.addWidget(self.create_btn)

    def _create_cam_layout(self):
        cam_layout = QtWidgets.QHBoxLayout()
        cam_layout.setSpacing(1)
        cam_layout.setContentsMargins(1, 1, 1, 1)

        camera_label = QtWidgets.QLabel(self.CAM_LABEL_TXT)
        cam_layout.addWidget(camera_label)

        self.camera_line_edit = QtWidgets.QLineEdit()
        self.camera_line_edit.setText(self.default_camera)
        self.camera_line_edit.setReadOnly(True)
        cam_layout.addWidget(self.camera_line_edit)

        self.get_selection_btn = QtWidgets.QPushButton(self.GET_CAM_TXT)
        cam_layout.addWidget(self.get_selection_btn)

        return cam_layout

    def ask_manual_mode(self):
        """
        Create a message box to ask the user for permission to continue.

        Return 'True' or 'False' depending on user input.
        :param str dialog_text: the question text to be displayed in the message box.
        :param str dialog_title: the title of the message box.
        """
        permission_box_text = "\n".join(
            [
                "The calculated camera translation is quite large.",
                "This may be due to large standin bounding boxes.",
                "\nDo you want to switch to manual translation?",
            ]
        )
        user_reply = message_box.permission_box(
            permission_box_text, self, "Switch to manual?"
        )
        if user_reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False


class ManualInterface(CyMayaWidget):
    """Create an manual interface window for the background creator tool."""

    OBJECT_NAME = "ManualInterface"
    WINDOW_TITLE = "Manual Interface"

    def __init__(self, center=True, parent=None):
        """Initialize class."""
        super(ManualInterface, self).__init__(center=center, parent=parent)
        self.default_camera = None
        self.create_btn = None
        self.get_selection_btn = None
        self.camera_line_edit = None
        self.smooth_slider = None

        self._init_main_layout()

    def _get_object_name(self):
        return self.OBJECT_NAME

    def _get_window_title(self):
        return self.WINDOW_TITLE

    def _init_main_layout(self):
        self.resize(420, 120)
        self.setWindowFlags(QtCore.Qt.Window)

        self.main_layout = QtWidgets.QGridLayout(self)
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(2, 2, 2, 2)

        self.translation_slider = FloatSliderWidget(
            min_value=0.0, max_value=100.0, start_value=100.0
        )
        self.main_layout.addWidget(self.translation_slider)


def main():
    """Initialize background creator view class."""
    view = BackgroundCreatorView()
    view.show()

    return view


if __name__ == "__main__":
    view = main()
