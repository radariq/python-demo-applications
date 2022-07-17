from math import tan, radians
from radariq import RadarIQ, MODE_OBJECT_TRACKING, OUTPUT_LIST, OBJECT_TYPE_PERSON

"""
Demonstration program counting people walking along a footpath etc.

This demonstration expects a person to walk in from the left or the right of the sensors field of view
and walk out the the other side. 
"""

FRAME_RATE = 5  # frames per second
MIN_DISTANCE = 1000  # Closest distance to look (mm)
MAX_DISTANCE = 10000  # Furthermost distance to look (mm)
MIN_ANGLE = -30  # Minimum angle to look
MAX_ANGLE = 30  # Maximum angle to look
OFFSET = 500  # fuzzy-matching the 'edge' of the sensors field of view.


class CountPeople:
    """
    Count people
    """

    def __init__(self):
        self.riq = None
        self.people = {}  # In the form {<object id> : 'left|right|counted'}
        self.counter = 0

    def start(self):
        """
        Start the visualization.
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
        Setup the RadarIQ module.
        """

        try:
            self.riq = RadarIQ(output_format=OUTPUT_LIST)
            self.riq.set_mode(MODE_OBJECT_TRACKING)
            self.riq.set_units('mm', 'mm/s')
            self.riq.set_frame_rate(FRAME_RATE)
            self.riq.set_object_type_mode(OBJECT_TYPE_PERSON)
            self.riq.set_distance_filter(MIN_DISTANCE, MAX_DISTANCE)
            self.riq.set_angle_filter(MIN_ANGLE, MAX_ANGLE)

        except Exception as error:
            print(error)

    def run_counter(self):
        for frame in self.riq.get_data():  # loop goes round once per frame
            if frame is not None:
                if frame['id'] in self.people.keys():  # has the person previously been detected
                    # person start on the left and is now at the right of the sensors field of view
                    if self.people[frame['id']] == 'left' and self.is_at_right_boundary(frame['x_pos'], frame['y_pos']):
                        self.people[frame['id']] = 'counted'
                        self.count()
                    # person start on the right and is now at the left of the sensors field of view
                    elif self.people[frame['id']] == 'right' and self.is_at_left_boundary(frame['x_pos'], frame['y_pos']):
                        self.people[frame['id']] = 'counted'
                        self.count()
                    # already counted. ignore
                    elif self.people[frame['id']] == 'counted':
                        pass
                else:  # New person
                    # If they are at the left boundary, begin counting them
                    if self.is_at_left_boundary(frame['x_pos'], frame['y_pos']):
                        self.people[frame['id']] = 'left'
                    # If they are at the right boundary, begin counting them
                    elif self.is_at_right_boundary(frame['x_pos'], frame['y_pos']):
                        self.people[frame['id']] = 'right'
                    # don't count at all until the object touches a boundary.
                    else:
                        pass

    def count(self):
        self.counter += 1
        print(self.counter)

    def is_at_left_boundary(self, x, y):
        """
        See if the object is on the left boundary.

        :param x: X coordinate of the object
        :param y: Y coordinate of the object
        :return:
        """
        x_boundary = tan(radians(MIN_ANGLE)) * y  # find where the x boundary would be for the objects y position
        x_boundary_1 = x_boundary - OFFSET
        x_boundary_2 = x_boundary + OFFSET

        # if the object is within the tolerance of the boundary
        return x_boundary_1 > x > x_boundary_2

    def is_at_right_boundary(self, x, y):
        """
        See if the object is on the right boundary.

        :param x: X coordinate of the object
        :param y: Y coordinate of the object
        :return:
        """
        x_boundary = tan(radians(MAX_ANGLE)) * y  # find where the x boundary would be for the objects y position
        x_boundary_1 = x_boundary - OFFSET
        x_boundary_2 = x_boundary + OFFSET

        # if the object is within the tolerance of the boundary
        return x_boundary_1 > x > x_boundary_2

    def exit_handler(self):
        """
        Catch the program exiting (ctrl C).
        """
        try:
            self.riq.close() # this will stop the sensor which will stop the run_counter loop
        except Exception:
            pass


if __name__ == '__main__':
    people_counter = CountPeople()
    people_counter.start()
