import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines
from numpy import c_
from math import tan, radians
import numpy as np

np.set_printoptions(suppress=True)


class PointCloud2D:
    def __init__(self, angle_min, angle_max, distance_min, distance_max, frame_rate, distance_units, data_getter):
        self.data_getter = data_getter
        self.plot_background_color = '#0033A0'
        self.point_size = 20
        self.elevation_angle = 15  # degrees
        self.running = True
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.plot_background_color)
        x_min = tan(radians(angle_min)) * distance_max
        x_max = tan(radians(angle_max)) * distance_max
        self.z_max = tan(radians(self.elevation_angle)) * distance_max
        self.ax.axis([x_min, x_max, distance_min, distance_max])
        self.ax.set_xlabel(f"x ({distance_units})")
        self.ax.set_ylabel(f"y ({distance_units})")
        self.cbar = None
        self.cmap = 'Reds'
        self.ax.grid(True)

        # Lines
        line1 = mlines.Line2D([0, x_min], [0, distance_max], color="silver", linewidth=1)
        line2 = mlines.Line2D([0, x_max], [0, distance_max], color="silver", linewidth=1)
        self.ax.add_line(line1)
        self.ax.add_line(line2)

        self.scat = self.ax.scatter([], [], s=self.point_size, c=[], cmap='Reds')

        # Double the frame rate to make sure it does not get behind. The module will control the actual frame rate
        frame_speed = 1000 / (frame_rate * 2)
        self.animation = animation.FuncAnimation(self.fig, self.update_plot, frames=self.fetch_data,
                                                 interval=frame_speed, init_func=self.init_plot, blit=True,
                                                 repeat=False, cache_frame_data=False)
        plt.show()

    def stop(self):
        self.running = False

    def fetch_data(self):
        for frame in self.data_getter():
            if self.running is True:
                yield frame
            else:
                break

    def init_plot(self):
        return self.scat,  # trailing comma is important

    def update_plot(self, frame):
        if frame:
            xs = [row[0] for row in frame]
            ys = [row[1] for row in frame]
            self.scat.set_offsets(c_[xs, ys])
            self.scat.set_sizes(np.full(len(frame), self.point_size))

            # Choose the dimension to show with color

            # color_dim = [row[2] for row in frame] # Height
            color_dim = [row[4] for row in frame]  # Velocity
            # color_dim = [row[3] for row in frame]  # Intensity

            self.scat.set_array(np.array(color_dim))

        return self.scat,  # trailing comma is important
