import matplotlib.lines as mlines
from radariq import RadarIQ, MODE_POINT_CLOUD, OUTPUT_LIST
import matplotlib.pyplot as plt
from matplotlib import animation
from numpy import c_

"""
Demonstration program plotting the doppler velocity against x position
"""

FRAME_RATE = 10  # frames per second
MIN_DISTANCE = 10  # Closest distance to look (mm)
MAX_DISTANCE = 2000  # Furthermost distance to look (mm)
MIN_ANGLE = -45  # Minimum angle to look - focus right in front of the sensor
MAX_ANGLE = 45  # Maximum angle to look - focus right in front of the sensor
SENSITIVITY = 8 # Low sensitivity


class Visualize:
    """
    Visualize Velocities of detected points.
    """

    def __init__(self):
        self.riq = None
        self.fig = None
        self.anim = None
        self.scat = None
        self.data = [[], []]

    def start(self):
        """
        Start the visualization.
        """
        try:
            self.setup_radariq()
            self.start_animation()
            self.riq.start()

        except Exception as err:
            print(err)
        finally:
            self.exit_handler()

    def setup_radariq(self):
        """
        Setup the RadarIQ module.
        """

        try:
            self.riq = RadarIQ(output_format=OUTPUT_LIST)
            self.riq.set_mode(MODE_POINT_CLOUD)
            self.riq.set_units('mm', 'mm/s')
            self.riq.set_frame_rate(FRAME_RATE)
            self.riq.set_distance_filter(MIN_DISTANCE, MAX_DISTANCE)
            self.riq.set_angle_filter(MIN_ANGLE, MAX_ANGLE)
            self.riq.set_certainty(SENSITIVITY)

        except Exception as error:
            print(error)

    def start_animation(self):
        frame_speed = (1000 / FRAME_RATE) / 2  # run the animation faster than the module
        self.fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)

        ax.axis([0, MAX_DISTANCE, -3000, 3000])
        ax.set_ylabel(f"Velocity (m/s)")
        ax.set_xlabel(f"Distance from Sensor (mm)")

        line1 = mlines.Line2D([0, MAX_DISTANCE], [0, 0], color="silver", linewidth=1)
        ax.add_line(line1)

        self.scat = ax.scatter([], [])
        self.riq.start()
        self.anim = animation.FuncAnimation(self.fig, self.update_plot, frames=self.riq.get_data, interval=frame_speed,
                                            init_func=self.init_plot, blit=True)
        plt.show()

    def init_plot(self):
        return self.scat,

    def update_plot(self, frame):
        if frame is not None:
            ys = [row[1] for row in frame]
            vs = [row[4] for row in frame]
            data = c_[ys, vs]
            print(data)
            self.scat.set_offsets(data)

        return self.scat,

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
