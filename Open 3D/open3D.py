import atexit
import open3d as o3d
import numpy as np
from math import tan, radians
from radariq import RadarIQ, MODE_POINT_CLOUD, OUTPUT_NUMPY

"""
Demonstration program connecting RadarIQ with Open3D
"""
FRAME_RATE = 5  # frames per second
MIN_DISTANCE = 10  # Closest distance to look (mm)
MAX_DISTANCE = 5000  # Furthermost distance to look (mm)
MIN_ANGLE = -45  # Minimum angle to look
MAX_ANGLE = 45  # Maximum angle to look
WINDOW_WIDTH = 1800  # Open3D window width
WINDOW_HEIGHT = 900  # Open3D window height


class Visualize:
    """
    Visualize RadarIQ data in 3D.
    """
    ELEVATION_ANGLE = 15  # Degrees

    def __init__(self):
        self.riq = None  # RadarIQ Object instance
        self.vis = None  # The Open3D Visualiser
        self.pts = None  # The point cloud shown in the Visualiser
        self.go_live()

    def go_live(self):
        """
        Start the visualization.
        """
        try:
            atexit.register(self.exit_handler)
            self.setup_radariq()
            self.start_visualiser()
            self.riq.start()

            for data in self.riq.get_data():
                print(data)
                self.visualise(data)

        except Exception as err:
            print(err)
        finally:
            self.exit_handler()

    def start_visualiser(self):
        """
        Start the Open3D Visualizer.
        """
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window("RadarIQ Point Cloud Visualiser", WINDOW_WIDTH, WINDOW_HEIGHT)
        self.pts = o3d.geometry.PointCloud()
        self.vis.add_geometry(self.pts)
        self.add_context()

        ctr = self.vis.get_view_control()
        parameters = o3d.io.read_pinhole_camera_parameters("CameraSettings.json")
        ctr.convert_from_pinhole_camera_parameters(parameters)

    def visualise(self, data):
        """
        Show the current point data (animation frame)
        :param data: The point cloud data from the RadarIQ API
        """
        self.pts.points = o3d.utility.Vector3dVector(data[:, :3])
        self.vis.update_geometry(self.pts)
        self.vis.poll_events()
        self.vis.update_renderer()

    def calculate_bounds(self):
        """
        Calculate the bounding box edges.
        """
        z_range = tan(radians(self.ELEVATION_ANGLE)) * MAX_DISTANCE

        xmin = tan(radians(MIN_ANGLE)) * MAX_DISTANCE
        xmax = tan(radians(MAX_ANGLE)) * MAX_DISTANCE
        ymin = MIN_DISTANCE
        ymax = MAX_DISTANCE
        zmin = -1 * z_range / 2
        zmax = z_range / 2


        return xmin, xmax, ymin, ymax, zmin, zmax

    def add_context(self):
        """
        Draw the bounding box, floor, and coordinate system.
        """

        xmin, xmax, ymin, ymax, zmin, zmax = self.calculate_bounds()
        points = [[xmin, ymin, zmin], [xmax, ymin, zmin], [xmin, ymax, zmin],
                  [xmax, ymax, zmin], [xmin, ymin, zmax], [xmax, ymin, zmax],
                  [xmin, ymax, zmax], [xmax, ymax, zmax]]

        lines = [[0, 1], [0, 2], [1, 3], [2, 3],
                 [4, 5], [4, 6], [5, 7], [6, 7],
                 [0, 4], [1, 5], [2, 6], [3, 7]]

        colors = [[1, 0, 0] for i in range(len(lines))]

        points = np.array(points)
        lines = np.array(lines)
        colors = np.array(colors)

        line_set = o3d.geometry.LineSet(
            points=o3d.utility.Vector3dVector(points),
            lines=o3d.utility.Vector2iVector(lines),
        )

        line_set.colors = o3d.utility.Vector3dVector(colors)
        self.vis.add_geometry(line_set)

        # Coordinate frame
        coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=500, origin=[-0, -0, -0])
        self.vis.add_geometry(coordinate_frame)

        # Floor
        mesh_box = o3d.geometry.TriangleMesh.create_box(width=(xmax - xmin), height=(ymax - ymin), depth=1)
        mesh_box.translate([xmin, 0, zmin])
        mesh_box.compute_vertex_normals()
        self.vis.add_geometry(mesh_box)

    def setup_radariq(self):
        """
        Setup the RadarIQ module.
        """

        try:
            self.riq = RadarIQ(output_format=OUTPUT_NUMPY)
            self.riq.set_mode(MODE_POINT_CLOUD)
            self.riq.set_units('mm', 'mm/s')
            self.riq.set_frame_rate(FRAME_RATE)
            self.riq.set_distance_filter(MIN_DISTANCE, MAX_DISTANCE)
            self.riq.set_angle_filter(MIN_ANGLE, MAX_ANGLE)

        except Exception as error:
            print(error)

    def exit_handler(self):
        """
        Catch the program exiting (ctrl C).
        """
        try:
            self.riq.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        Visualize()
    except KeyboardInterrupt:
        print("Exit")
        pass
