"""Constants relevant for background creator."""

# nodes
RESOLUTION_NODE = 'defaultResolution'
BACKGROUND_CAM_NAME = 'BG_cam'

# errors
NO_CAM_ERROR = 'Please select one camera'

# ui
NO_CAM_MSG_TITLE = 'Selection Error'
MAIN_PANE = 'MainPane'

# numerical constants
FRAME_RANGE_THRESHOLD = 100
INCH_TO_MM_RATIO = 0.039370078740157
RANGE_DIVISION_FACTOR = 4
MAXIMUM_RENDER_WIDTH = 7680

# attributes
FOCAL_LENGTH_ATTR = '{}.focalLength'
HORIZONTAL_APERTURE_ATTR = '{}.horizontalFilmAperture'
RENDER_ASPECT_RATIO_ATTR = '{}.deviceAspectRatio'.format(RESOLUTION_NODE)
RESOLUTION_HEIGHT_ATTR = '{}.height'.format(RESOLUTION_NODE)
RESOLUTION_WIDTH_ATTR = '{}.width'.format(RESOLUTION_NODE)
VERTICAL_APERTURE_ATTR = '{}.verticalFilmAperture'

# miscelaneous
ADDITION_OPERATOR = 'add'
SUBTRACTION_OPERATOR = 'subtract'

# object types
DISPLAY_OBJ_TYPES = ['mesh']

# dictionary keys
CAM_COORDINATES_KEY = 'cam coordinates'
COI_VECTOR_KEY = 'coi vector'
FRAME_KEY = 'frame'
COI_KEY = 'coi'
WORLDUP_KEY = 'worldup'
DEPTH_VECTOR_KEY = 'depth vector'
