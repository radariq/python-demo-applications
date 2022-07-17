import time


class VisualisationBase:
    """
    Base class which all visualisations inherit
    """
    elevation_angle = 15  # degrees

    def __init__(self, data_getter):
        self.data_getter = data_getter  # @todo not sure about th use of timeout
        self.canvas = None
        self.animation = None
        self.render_speed = 0.0
        self.last_frame_time = 0

        self.plot_background_color = '#0033A0'
        self.point_size = 20

        self.running = True

    def stop(self):
        self.running = False

    def remove(self):
        """
        Remove any additional components
        """
        pass

    def get_canvas(self):
        return self.canvas.get_tk_widget()

    def fetch_data(self):
        for frame in self.data_getter():
            if self.running is True:
                yield frame
            else:
                break

    def measure_render_speed(self):
        now = time.time()
        self.render_speed = now - self.last_frame_time
        self.last_frame_time = now

    def get_rendered_frame_rate(self):
        return round(1/self.render_speed)
