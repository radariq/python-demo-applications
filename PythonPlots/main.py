from radariq import RadarIQ, MODE_OBJECT_TRACKING, MODE_POINT_CLOUD, OUTPUT_LIST
from visualisations.ObjectPlot2D import ObjectPlot2D
from visualisations.PointCloud2D import PointCloud2D

"""
Demonstration program plotting radarIQ data
"""

FRAME_RATE = 10  # frames per second
MIN_DISTANCE = 100  # Closest distance to look (mm)
MAX_DISTANCE = 10000  # Furthermost distance to look (mm)
MIN_ANGLE = -45  # Minimum angle to look
MAX_ANGLE = 45  # Maximum angle to look
MODE = MODE_OBJECT_TRACKING


class Visualize:
    """
    Visualize Paths using RadarIQ's object tracking mode.
    """

    def __init__(self):
        self.riq = None

    def start(self):
        """
        Start the visualization.
        """
        try:
            self.setup_radariq()
            self.riq.start()
            if MODE == MODE_POINT_CLOUD:
                self.visualisation = PointCloud2D(angle_min=MIN_ANGLE, angle_max=MAX_ANGLE,
                                                  distance_min=MIN_DISTANCE, distance_max=MAX_DISTANCE,
                                                  frame_rate=FRAME_RATE, distance_units='mm',
                                                  data_getter=self.riq.get_data)
            elif MODE == MODE_OBJECT_TRACKING:
                self.visualisation = ObjectPlot2D(angle_min=MIN_ANGLE, angle_max=MAX_ANGLE,
                                                  distance_min=MIN_DISTANCE, distance_max=MAX_DISTANCE,
                                                  frame_rate=FRAME_RATE, distance_units='mm',
                                                  data_getter=self.riq.get_data)

        except Exception as err:
            print(err)
        finally:
            self.exit_handler()

    def setup_radariq(self):
        """
        Set up the RadarIQ module.
        """

        try:
            self.riq = RadarIQ(output_format=OUTPUT_LIST)
            self.riq.set_mode(MODE)
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


if __name__ == '__main__':
    vis = Visualize()
    vis.start()
