import math

from MaxSandbox.background_creator import constants, utils
from maya import cmds


class BackgroundCreatorModel(object):
    """Business logic of background creator tool."""

    def __init__(self):
        self.horizontal_aperture = None
        self.vertical_aperture = None
        self.horizontal_aov = None
        self.vertical_aov = None

    def calculate_cam_translation(self, camera_shape, camera_transform, stereo_cam=False):
        """
        Create background camera which has all geometric objects in its field of view.

        Do this using the smallest translation of the camera possible.
        :param str camera_shape: shape node of camera
        :param str camera_transform: transform node of camera
        Returns None
        """
        # get current render settings
        aspect_ratio, resolution = self._fetch_render_settings()

        # get camera settings
        self.horizontal_aperture, self.vertical_aperture = self._fetch_aperture(camera_shape)
        self.horizontal_aperture = self._calculate_correct_aperture(aspect_ratio, self.vertical_aperture)
        self._set_correct_aperture(camera_shape, self.horizontal_aperture)
        self.horizontal_aov, self.vertical_aov = self._fetch_camera_settings(camera_shape,
                                                                             self.horizontal_aperture,
                                                                             self.vertical_aperture)

        # get frame range
        frame_range = self._fetch_frame_range()

        # if frame range is very large, shrink it
        if len(frame_range) > constants.FRAME_RANGE_THRESHOLD:
            print '// slicing frame range'
            new_frame_range = []
            for i, frame in enumerate(frame_range):
                if i % constants.RANGE_DIVISION_FACTOR == 0:
                    new_frame_range.append(frame)
            print '// sliced frame range:', str(new_frame_range)
            frame_range = new_frame_range

        # get vertices in view of source camera
        vertices_in_view = list()
        for frame in frame_range:
            cmds.currentTime(frame)
            current_vertices = utils.fetch_vertices_in_view()
            for vertex in current_vertices:
                if vertex not in vertices_in_view:
                    vertices_in_view.append(vertex)

        # get vertex coordinates
        vtx_coordinates = utils.fetch_vtx_coordinates(vertices_in_view)

        # check which on which frame the smallest amount of camera translation is required to get all display objects into view
        cam_translation_dict = {}
        for frame in frame_range:
            cmds.currentTime(frame)

            current_frame_translation, current_cam_coordinates, coi_vector, average_depth_vector = self.calc_cam_translation(
                camera_shape, camera_transform, aspect_ratio, vtx_coordinates)
            cam_translation_dict[current_frame_translation] = {constants.FRAME_KEY: frame,
                                                               constants.CAM_COORDINATES_KEY: current_cam_coordinates,
                                                               constants.COI_VECTOR_KEY: coi_vector,
                                                               constants.DEPTH_VECTOR_KEY: average_depth_vector}
        cam_translation = min(cam_translation_dict.keys())

        resolution = self._calculate_new_resolution(resolution, average_depth_vector, cam_translation, aspect_ratio)

        return cam_translation, cam_translation_dict[cam_translation], aspect_ratio, resolution

    def init_background_cam(self, cam_translation, cam_translation_dict, aspect_ratio, resolution, camera_transform):
        """Fetch camera settings and create background camera."""
        # fetch all other camera settings from cam_translation_dict0
        current_cam_coordinates = cam_translation_dict[constants.CAM_COORDINATES_KEY]
        coi_vector = cam_translation_dict[constants.COI_VECTOR_KEY]
        optimal_frame = cam_translation_dict[constants.FRAME_KEY]
        average_depth_vector = cam_translation_dict[constants.DEPTH_VECTOR_KEY]

        # create background camera with optimal translation
        camera = self.create_camera(optimal_frame, current_cam_coordinates, camera_transform)

        # calculate new camera position
        new_cam_position = self._calculate_new_cam_position(current_cam_coordinates, cam_translation, coi_vector)

        # move camera
        self._move_camera(camera, new_cam_position)

        # calculate and apply new render resolution, to compensate for camera translation
        new_resolution = self._calculate_new_resolution(resolution, average_depth_vector, cam_translation, aspect_ratio)
        self._apply_resolution(new_resolution, aspect_ratio)

        return coi_vector, current_cam_coordinates, new_cam_position, camera

    def calc_cam_translation(self, camera_shape, camera_transform, aspect_ratio, vtx_coordinates):
        """
        Calculate the minimal translation along the camera's z-axis required to bring all display objects into view.

        :param str camera_shape: the camera's shape node.
        :param str camera_transform: the camera's transform node.
        """
        # coordinates of camera transform
        cam_coordinates = self._fetch_cam_coordinates(camera_transform)

        # center of interest of camera
        center_of_interest = self._fetch_center_of_interest(camera_shape)

        # calculate distance from camera to center of interest
        coi_cam_dist = self.calculate_3d_distance(cam_coordinates, center_of_interest)

        # fetch camera's world-up vector
        cam_world_up = self._fetch_worldup_vector(camera_transform)

        # calculate vector for camera-coi line
        coi_vector = self._calculate_coi_vector(cam_coordinates, center_of_interest, coi_cam_dist)

        # calculate required camera offset for each display object.
        cam_translation = 0
        vector_depth_values = []
        for vertex in vtx_coordinates:
            # calculate distance between vertex, coi and camera
            cam_vtx_dist = self.calculate_3d_distance(vertex, cam_coordinates)
            coi_vtx_dist = self.calculate_3d_distance(vertex, center_of_interest)

            # calculate depth component of vector from camera to given vertex
            vector_depth, depth_triangle_height, depth_height_intersect = self._calculate_vector_depth(cam_vtx_dist, coi_vtx_dist,
                                                                                                       coi_cam_dist, center_of_interest,
                                                                                                       cam_coordinates,
                                                                                                       coi_vector)

            # deduce width and height components of cam-vertex vector
            vtx_angle = self._calculate_vtx_angle(vertex, cam_world_up, constants.SUBTRACTION_OPERATOR, depth_height_intersect,
                                                  depth_triangle_height)
            vector_height, vector_width = self._fetch_width_and_height_vectors(depth_triangle_height, cam_world_up, vertex, vtx_angle)

            # calculate camera translation required to bring vertex into view
            cam_translation_horizontal = self._calculate_camera_offset(vector_depth, vector_width, self.horizontal_aov)
            cam_translation_vertical = self._calculate_camera_offset(vector_depth, vector_height, self.vertical_aov)

            # add current vector depth value to list
            vector_depth_values.append(vector_depth)

            # if cam translation for current vertex is larger than for previous vertex, update cam translation.
            # use the largest translation value, to ensure the vertex is in view.
            if cam_translation_horizontal > cam_translation_vertical and cam_translation_horizontal > cam_translation:
                cam_translation = cam_translation_horizontal
            elif cam_translation_vertical > cam_translation:
                cam_translation = cam_translation_vertical

        sum_vector_depth = 0
        for value in vector_depth_values:
            sum_vector_depth += value
        average_vector_depth = sum_vector_depth / len(vector_depth_values)
        return cam_translation, cam_coordinates, coi_vector, average_vector_depth

    def _calculate_new_resolution(self, resolution, average_depth_vector, cam_translation, aspect_ratio):
        """
        Calculate and apply new render resolution, to compensate for camera translation.

        :param list resolution: current render resolution
        :param float average_depth_vector: average depth vector from camera to vertices.
        :param float cam_translation: magnitude of camera translation
        Returns new render resolution
        """
        # print 'average depth vector:', str(average_depth_vector)
        # print 'cam translation:', str(cam_translation)
        scale_ratio = (abs(average_depth_vector) + cam_translation) / abs(average_depth_vector)
        # print 'scale ratio:', str(scale_ratio), '<----------------------------'
        x_dimension = float(resolution[0]) * scale_ratio

        # if x dimension is greater than maximum width, cap render resolution
        if x_dimension > constants.MAXIMUM_RENDER_WIDTH:
            x_dimension = constants.MAXIMUM_RENDER_WIDTH
            y_dimension = float(x_dimension) / aspect_ratio
        else:
            y_dimension = float(resolution[1]) * scale_ratio
        new_resolution = [x_dimension, y_dimension]
        return new_resolution

    def _fetch_cam_coordinates(self, camera_transform):
        cam_coordinates = cmds.xform(camera_transform, query=True, translation=True, worldSpace=True)
        return cam_coordinates

    def fetch_selected_cam(self):
        """
        Get selected camera.

        Returns camera transform and shape nodes, unless more than one camera is selected, or
        none are selected. In these cases, returns None.
        """
        # make dict of selected camera, containing camera shape and transform
        selection = cmds.ls(selection=True)
        all_cameras = cmds.ls(cameras=True)
        cam_shape = None
        cam_transform = None
        for cam in all_cameras:
            transform = cmds.listRelatives(cam, parent=True)[0]
            if transform in selection:
                # check if there is already a selected camera in the selection list
                if cam_shape is not None:
                    return None, None
                else:
                    cam_shape = cam
                    cam_transform = transform
        return cam_transform, cam_shape

    def _fetch_aperture(self, camera):
        """Fetch horizontal and vertical aperture in millimeters."""
        horizontal_aperture = cmds.camera(camera, query=True, horizontalFilmAperture=True) / constants.INCH_TO_MM_RATIO
        vertical_aperture = cmds.camera(camera, query=True, verticalFilmAperture=True) / constants.INCH_TO_MM_RATIO
        return horizontal_aperture, vertical_aperture

    def _fetch_camera_settings(self, camera, horizontal_aperture, vertical_aperture):
        """
        Fetch horizontal and vertical angles of view for the given camera.

        :param str camera: camera selected by user.
        :param float vertical_aperture: vertical aperture of given camera.
        :param float horizontal_aperture: horizontal aperture of given camera.
        Returns horizontal and vertical angles of view of camera.
        """
        horizontal_angle_of_view = cmds.camera(camera, query=True, horizontalFieldOfView=True)
        vertical_angle_of_view = cmds.camera(camera, query=True, verticalFieldOfView=True)
        return horizontal_angle_of_view, vertical_angle_of_view

    def _fetch_frame_range(self):
        """Create a list of all frame numbers in the time slider."""
        first_frame = cmds.playbackOptions(query=True, minTime=True)
        last_frame = cmds.playbackOptions(query=True, maxTime=True)

        frame_range = []
        i = first_frame
        while i < last_frame:
            frame_range.append(i)
            i += 1
        return frame_range

    def _fetch_center_of_interest(self, camera):
        """Fetch worldspace coordinates of camera's center of interest point."""
        center_of_interest = cmds.camera(camera, query=True, worldCenterOfInterest=True)
        return center_of_interest

    def _fetch_render_settings(self):
        """Fetch aspect ratio of render settings resolution."""
        resolution_width = cmds.getAttr(constants.RESOLUTION_WIDTH_ATTR)
        resolution_height = cmds.getAttr(constants.RESOLUTION_HEIGHT_ATTR)
        resolution = [resolution_width, resolution_height]
        aspect_ratio = cmds.getAttr(constants.RENDER_ASPECT_RATIO_ATTR)
        return aspect_ratio, resolution

    def _fetch_worldup_vector(self, camera):
        """Fetch the camera's world-up vector."""
        cam_world_up = cmds.camera(camera, query=True, worldUp=True)
        return cam_world_up

    def _calculate_correct_aperture(self, aspect_ratio, vertical_aperture):
        """Calculate new aperture based on render settings aspect ratio."""
        new_horizontal_aperture = vertical_aperture * aspect_ratio
        return new_horizontal_aperture

    def _calculate_camera_offset(self, vector_depth, opposite_side, camera_angle_of_view):
        """
        Calculate required camera offset for the given object.

        Camera offset refers to the relative translation along the camera's Z-axis, needed to bring the object into view.
        """
        # calculate third angle of right angled triangle
        # third_angle = constants.RIGHT_ANGLE_RADIANS - math.radians(camera_angle_of_view)

        # calculate minimum required depth vector length.
        minim_depth = opposite_side / math.tan(math.radians(camera_angle_of_view / 2))
        if minim_depth >= vector_depth:
            camera_translation = minim_depth - vector_depth
            return camera_translation
        else:
            return 0

    def _calculate_coi_vector(self, camera_position, center_of_interest, coi_cam_dist):
        """
        Calculate the vector of the coi-camera line.

        :param list camera_position: worldspace position of camera.
        :param list center_of_interest: worldspace position of camera's center of interest point.
        """
        coi_vector = []
        for cam_coordinate, coi_coordinate in zip(camera_position, center_of_interest):
            # calculate component of coi-cam vector
            vector_component = (cam_coordinate - coi_coordinate) / coi_cam_dist
            coi_vector.append(vector_component)
        return coi_vector

    def calculate_3d_distance(self, first_point, second_point):
        """
        Calculate distance between two points in worldSpace.

        :param list first_point: worldspace coordinates of first point.
        :param list second_point: worldspace coordinates of second point.
        """
        # calculate distances along x, y, z - axes
        x_dist = abs(first_point[0] - second_point[0])
        y_dist = abs(first_point[1] - second_point[1])
        z_dist = abs(first_point[2] - second_point[2])

        # calculate distance on xz-plane
        xz_dist = math.hypot(x_dist, z_dist)

        # calculate distance in 3d space
        dist_3d = math.hypot(xz_dist, y_dist)
        return dist_3d

    def _calculate_vector_depth(self, cam_vtx_dist, coi_vtx_dist, coi_cam_dist, center_of_interest, camera_position, coi_vector):
        """
        Calculate the depth component of the vector cam-vtx.

        Return the depth component itself, and the height of the triangle it forms with the camera's z-axis and the vtx-cam line.
        """
        # calculate angle of point 'cam' in the triangle 'coi-cam-vtx'.
        cam_angle = math.acos((coi_cam_dist**2 + cam_vtx_dist**2 - coi_vtx_dist**2) / (2 * coi_cam_dist * cam_vtx_dist))

        # calculate depth component (adjacent to cam angle) and depth_triangle_height (opposite to cam angle)
        #       if cam angle is greater than 90 degrees (or 0.5pi), use the complementary angle.
        # if cam_angle >= (math.pi / 2):
        #     cam_angle = math.pi - cam_angle
        vector_depth = cam_vtx_dist * math.cos(cam_angle)
        depth_triangle_height = vector_depth * math.tan(cam_angle)

        # calculate worldspace position of the intersect point between vector_depth and depth_triangle_height
        depth_height_intersect = []
        for cam_coordinate, vector_component in zip(camera_position, coi_vector):
            # multiply vector by depth component length and subtract from cam position to arrive at intersect-coordinate
            intersect_coordinate = cam_coordinate - (vector_component * vector_depth)
            depth_height_intersect.append(intersect_coordinate)

        return vector_depth, depth_triangle_height, depth_height_intersect

    def _calculate_new_cam_position(self, camera_position, cam_translation, coi_vector):
        """
        Calculate the new camera position.

        :param list camera_position: worldspace position of camera
        """
        new_cam_position = []
        for cam_coordinate, vector_component in zip(camera_position, coi_vector):
            intersect_coordinate = cam_coordinate + (vector_component * cam_translation)
            new_cam_position.append(intersect_coordinate)
        return new_cam_position

    def _calculate_vtx_angle(self, vertex, cam_world_up, operator, depth_height_intersect, depth_triangle_height):
        """
        Calculate the angle between the camera's worldup vector and the coi-vtx line.

        :param list vertex: worldspace coordinates of given bounding box vertex.
        :param list cam_world_up: camera's worldup vector.
        """
        # Create a point on the camera's world up vector which has a distance to the vertex of exactly 1, and
        # calculate the point's worldspace position
        worldup_point = []
        for vtx_coordinate, vector_axis in zip(vertex, cam_world_up):
            if operator == constants.SUBTRACTION_OPERATOR:
                point_coordinate = vtx_coordinate - vector_axis
            else:
                point_coordinate = vtx_coordinate + vector_axis
            worldup_point.append(point_coordinate)
        # calculate distance from worldup point to camera's center of interest
        intersect_wup_dist = self.calculate_3d_distance(worldup_point, depth_height_intersect)

        # calculate angle between vertex-worldup_point line and the vertex-coi line.
        # print 'intersect_wup_dist:', str(intersect_wup_dist)
        # print 'depth_triangle_height', str(depth_triangle_height)
        vtx_angle = math.acos((1 + depth_triangle_height**2 - intersect_wup_dist**2) / (2 * depth_triangle_height))

        # check if vtx_angle is greater than 90 degrees(or 0.5pi radians).
        # If so, calculate vtx angle again using addition operator.
        if vtx_angle > (math.pi / 2) and operator == constants.SUBTRACTION_OPERATOR:
            vtx_angle = self._calculate_vtx_angle(vertex, cam_world_up, constants.ADDITION_OPERATOR, depth_height_intersect, depth_triangle_height)
            return vtx_angle
        else:
            return vtx_angle

    def _fetch_width_and_height_vectors(self, depth_triangle_height, cam_world_up, vertex, vtx_angle):
        """
        Split vector from camera to given vertex into two separate vectors and return their lengths.

        One vector is parallel to the camera's world-up vector and the other is perpendicular to it.
        """
        # the two vectors we are looking for form a right-angled triangle with the coi-vtx line.
        # calculate the angle of the coi-point in this triangle(in radians).
        coi_angle = math.pi / 2 - vtx_angle

        # calculate the length of the other 2 sides of the triangle. These are the split vectors.
        vector_height = depth_triangle_height * math.sin(coi_angle)
        vector_width = depth_triangle_height * math.sin(vtx_angle)
        return vector_height, vector_width

    def _set_correct_aperture(self, camera, horizontal_aperture):
        """
        Set the new aperture of the given camera.

        :param str camera: camera selected by user.
        :param float horizontal_aperture: horizontal aperture of given camera.
        """
        horizontal_aperture = constants.INCH_TO_MM_RATIO * horizontal_aperture
        cmds.setAttr(constants.HORIZONTAL_APERTURE_ATTR.format(camera), horizontal_aperture)

    def create_camera(self, frame, old_cam_position, camera_transform):
        """Go to most optimal frame, move camera and duplicate it."""
        cmds.currentTime(frame)

        # get cam orientation
        cam_orientation = cmds.xform(camera_transform, query=True, rotation=True, worldSpace=True)

        # create new camera and give it the new cam orientation
        new_camera = cmds.camera(name=constants.BACKGROUND_CAM_NAME)[0]
        cmds.rotate(cam_orientation[0], cam_orientation[1], cam_orientation[2], new_camera, absolute=True)

        # set aperture settings on newly created background camera
        horizontal_aperture = self.horizontal_aperture * constants.INCH_TO_MM_RATIO
        vertical_aperture = self.vertical_aperture * constants.INCH_TO_MM_RATIO
        focal_length = cmds.getAttr(constants.FOCAL_LENGTH_ATTR.format(camera_transform))
        cmds.setAttr(constants.HORIZONTAL_APERTURE_ATTR.format(new_camera), horizontal_aperture)
        cmds.setAttr(constants.VERTICAL_APERTURE_ATTR.format(new_camera), vertical_aperture)
        cmds.setAttr(constants.FOCAL_LENGTH_ATTR.format(new_camera), focal_length)

        # look through new camera
        cmds.lookThru(new_camera)

        return new_camera

    def _move_camera(self, camera, new_position):
        cmds.move(new_position[0], new_position[1], new_position[2], camera, absolute=True)

    def _apply_resolution(self, new_resolution, aspect_ratio):
        """Apply the new resolution."""
        cmds.setAttr(constants.RESOLUTION_WIDTH_ATTR, new_resolution[0])
        cmds.setAttr(constants.RESOLUTION_HEIGHT_ATTR, new_resolution[1])
        cmds.setAttr(constants.RENDER_ASPECT_RATIO_ATTR, aspect_ratio)

    def manually_translate_cam(self, translation_value, coi_vector, current_cam_coordinates, camera):
        """Give the given camera the given translation."""
        # calculate new camera position
        new_cam_position = self._calculate_new_cam_position(current_cam_coordinates, translation_value, coi_vector)
        self._move_camera(camera, new_cam_position)
