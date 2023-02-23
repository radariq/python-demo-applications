from math import tan, radians
from radariq import RadarIQ, MODE_POINT_CLOUD, OUTPUT_LIST, MOVING_OBJECTS_ONLY, DENSITY_VERY_DENSE

"""
Demonstration program counting people walking along a footpath etc.

This demonstration expects a person to walk in from either the left or the right of the sensors field of view
and walk out the other side. This works best when the person is about 5m away from the sensor.

This implementation uses the point cloud application to count people.

This program sets up a zone on the left boundary of the sensor and a similar zone on the right side of the sensor.
When a person enters or exits one of these this gets recorded as a 'left-enter', 'left-exit', 'right-enter', 'right-exit'

Tips for usage:
1. Run this application once. This will set the relevant parameters on the sensor.
2. Open the RadarIQ Controller Application to visualise what the sensor is seeing. This will allow you to see the 
edges of the detection zone. Once you've done this close the RadarIQ Controller.
3. Run this application again and walk in and out of the areas you identified in step 2.
"""

FRAME_RATE = 10  # frames per second
MIN_DISTANCE = 2000  # Closest distance to look (mm)
MAX_DISTANCE = 8000  # Furthermost distance to look (mm)
MIN_ANGLE = -30  # Minimum angle to look
MAX_ANGLE = 30  # Maximum angle to look
MARGIN = 500
THRESHOLD = 10


class CountPeople:
    """
    Count people
    """

    def __init__(self):
        self.riq = None
        self.counter = {'left-enter': 0,
                        'left-exit': 0,
                        'right-enter': 0,
                        'right-exit': 0
                        }
        self.left_detected = False
        self.right_detected = False
        self.min_angle_tan = tan(radians(MIN_ANGLE))
        self.max_angle_tan = tan(radians(MAX_ANGLE))

    def start(self):
        """
        Start the sensor and the application.
        """
        try:
            self.setup_radariq()
            self.riq.start()
            self.run_counter()

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
            self.riq.set_mode(MODE_POINT_CLOUD)
            self.riq.set_units('mm', 'mm/s')
            self.riq.set_frame_rate(FRAME_RATE)
            self.riq.set_moving_filter(MOVING_OBJECTS_ONLY)
            self.riq.set_sensitivity(3)
            self.riq.set_point_density(DENSITY_VERY_DENSE)
            self.riq.set_distance_filter(MIN_DISTANCE, MAX_DISTANCE)
            self.riq.set_angle_filter(MIN_ANGLE, MAX_ANGLE)

        except Exception as error:
            print(error)

    def run_counter(self):
        for points in self.riq.get_data():  # loop goes round once per frame
            if points is not None:
                left = self.count_at_left_boundary(points)
                if self.left_detected is False and left > THRESHOLD:
                    self.left_detected = True
                    self.count('left-enter')
                elif self.left_detected is True and left < THRESHOLD:
                    self.left_detected = False
                    self.count('left-exit')

                right = self.count_at_right_boundary(points)
                if self.right_detected is False and right > THRESHOLD:
                    self.right_detected = True
                    self.count('right-enter')
                elif self.right_detected is True and right < THRESHOLD:
                    self.right_detected = False
                    self.count('right-exit')

    def count(self, state):
        self.counter[state] += 1

        print(self.counter)

    def count_at_left_boundary(self, points):
        """
        Count the number of points at the left boundary
        """
        count = 0
        for point in points:
            y = point[1]
            x = point[0]
            x_boundary = self.min_angle_tan * y  # find where the x boundary would be for the objects y position
            x_boundary_1 = x_boundary - MARGIN
            x_boundary_2 = x_boundary + MARGIN
            if x_boundary_1 < x < x_boundary_2:
                count += 1

        return count

    def count_at_right_boundary(self, points):
        """
        Count the number of points at the right boundary
        """
        count = 0
        for point in points:
            y = point[1]
            x = point[0]
            x_boundary = self.max_angle_tan * y  # find where the x boundary would be for the objects y position
            x_boundary_1 = x_boundary - MARGIN
            x_boundary_2 = x_boundary + MARGIN

            if x_boundary_1 < x < x_boundary_2:
                count += 1

        return count

    def exit_handler(self):
        """
        Catch the program exiting (ctrl C).
        """
        try:
            self.riq.close()  # this will stop the sensor which will stop the run_counter loop
        except Exception:
            pass


if __name__ == '__main__':
    people_counter = CountPeople()
    people_counter.start()
