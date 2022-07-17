import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.animation as animation
import matplotlib as mpl


from numpy import c_
from math import tan, radians
from visualisations.VisualisationBase import VisualisationBase


class ModObjectPlot2D(VisualisationBase):
    """
    2D Object plot
    """

    def __init__(self, data_getter, settings, device):
        VisualisationBase.__init__(self, data_getter)
        
        # Start Devices
        self.plt = plt
        self.device = device
        self.device.start()

        # Debug
        self.start_time = time.time()
        self.end_time = 0

        # Plot Initializations

        self.settings = settings
        self.max_objects = 10
        self.colors = ['#008000', '#ff0000', '#ffff00', '#00ff00', '#8b4513',
                       '#00ffff', '#ff00ff', '#6495ed', '#ff69b4', '#ffe4c4']
        self.show_tails = False
        self.tail_length = 1
        self.max_point_size = 200
        self.selected_object = None

        self.object_map = [None] * self.max_objects
        self.path_history = []
        for i in range(self.max_objects):
            self.path_history.append(
                np.full((self.tail_length, 2), -1000))  # populate with points off the side of the graph to hide them
        # Plots
        mpl.rcParams['toolbar'] = 'None'
        self.fig = self.plt.figure()
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_facecolor(self.plot_background_color)
        x_min = tan(radians(settings['angle_min'])) * settings['distance_max']
        x_max = tan(radians(settings['angle_max'])) * settings['distance_max']
        self.ax.axis([x_min, x_max, settings['distance_min'], settings['distance_max']])
        self.ax.set_xlabel(f"x ({settings['distance_units']})")
        self.ax.set_ylabel(f"y ({settings['distance_units']})")
        self.ax.grid(True)

        # Lines
        line1 = mlines.Line2D([0, x_min], [0, settings['distance_max']], color="silver", linewidth=1)
        line2 = mlines.Line2D([0, x_max], [0, settings['distance_max']], color="silver", linewidth=1)
        self.ax.add_line(line1)
        self.ax.add_line(line2)

        self.scats = []
        for i in range(self.max_objects):
            self.scats.append(self.ax.scatter([], [], c=self.colors[i], picker=True))

        self.fig.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.88)

        # Double the frame rate to make sure it does not get behind. The module will control th actual frame rate
        frame_speed = 1000 / (settings['frame_rate'] * 2)
        self.animation = animation.FuncAnimation(self.fig, self.update_plot, frames=self.fetch_data,
                                                 interval=frame_speed,
                                                 repeat=False, cache_frame_data=False)

    def show(self):
        """
        Displays the visualization in its own window
        """
        self.plt.title("Detected Objects")
        self.plt.show()

    def __del__(self):
        # @todo don't know if this is actually deleting
        print("deleted")

    def update_plot(self, frame):
        """
        Updates the plot during animation.

        :param frame: Incoming frame data
        :return: array of series on the plot
        """
        # Roll all plots
        raw_frame = frame

        self.process_radar_frame(raw_frame)
        return self.scats,

    def get_plot_index(self, object_index):
        """
        Get the scatter plot index. This may or may not be the index of the object
        """
        # Look for existing mapping between object id and scatter plot
        for scat_idx, obj_idx in enumerate(self.object_map):
            if obj_idx == object_index:
                return scat_idx

        # Assign the object index to a scatter plot index if the mapping does not exist
        for scat_idx, obj_idx in enumerate(self.object_map):
            if obj_idx is None:
                self.object_map[scat_idx] = object_index
                return scat_idx

        # Clean out unused slots and try and assign again
        # It is advisable to keep slots open as long as possible before reassigning them
        # Try again to assign the object index to a scatter plot index if the mapping does not exist
        for scat_idx in range(self.max_objects):
            if np.count_nonzero(self.path_history[scat_idx]) == 0:  # All points are zero
                self.object_map[scat_idx] = None

        for scat_idx, obj_idx in enumerate(self.object_map):
            if obj_idx is None:
                self.object_map[scat_idx] = object_index
                return scat_idx

        return None  # No available slots

    def process_radar_frame(self, frame):
        for idx in range(self.max_objects):
            self.path_history[idx] = np.roll(self.path_history[idx], 2)  # array is 2 wide

        if frame is not None:
            used_idxs = []  # keeps track of the indexes which are still used.
            for obj in frame:
                idx = self.get_plot_index(obj['tracking_id'])
                used_idxs.append(idx)
                if idx is not None:
                    self.path_history[idx][0] = [obj['x_pos'], obj['y_pos']]

                    self.scats[idx].set_offsets(c_[self.path_history[idx][0:self.tail_length, 0],
                                                   self.path_history[idx][0:self.tail_length, 1]])

                # Clean up plots which are no longer used
                for idx in range(len(self.scats)):
                    if idx not in used_idxs:
                        self.scats[idx].set_offsets(c_[[],[]])

        return self.scats
