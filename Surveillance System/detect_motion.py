from radariq.RadarIQ import RadarIQ, OUTPUT_LIST, MODE_OBJECT_TRACKING
import time


class DetectMotion:
    def __init__(self):
        self.triggered = False
        self.device = RadarIQ(output_format=OUTPUT_LIST)

        # RadarIQ module variable
        self.sleep = 0.2
        self.sensitivity = 5

        # RadarIQ setting for initialization
        self.settings = {
            'distance_units': "mm",
            'speed_units': "m/s",
            'acceleration_units': "mm/s²",
            'distance_min': 0.0,
            'distance_max': 6000.0,
            'angle_min': -55,
            'angle_max': 55,
            'height_min': -1000.00,
            'height_max': 1000.00,
            'frame_rate': 20
        }

        # Start Module
        self.data_stream = None
        self.initialize_module()

        # Stop global
        self.stopped = False

    def initialize_module(self):
        self.device.connection.flush_all()

        self.device.stop()
        self.device.set_mode(MODE_OBJECT_TRACKING)
        self.device.set_units('mm', 'mm/s')
        self.device.set_frame_rate(self.settings['frame_rate'])
        self.device.set_distance_filter(self.settings['distance_min'], self.settings['distance_max'])
        self.device.set_angle_filter(self.settings['angle_min'], self.settings['angle_max'])
        self.device.set_height_filter(self.settings['height_min'], self.settings['height_max'])
        self.device.set_sensitivity(self.sensitivity)

    def start(self):
        print("A")
        # Start the module and start data capture
        self.device.start()
        print("[INFO] RadarIQ Started")
        print("[INFO] Motion Capture Started")

        previous_frame = []
        self.stopped = False

        # Process Frame For Detection
        while not self.stopped:
            curr_time = time.time()
            curr_frame = self.device.get_frame()

            if previous_frame:
                # Check if any object from curr frame where in previous frames
                for prev_obj in previous_frame:
                    track_id = prev_obj["tracking_id"]
                    if curr_frame:
                        for curr_obj in curr_frame:
                            # If a matching object is found check if the object has been there for longer than 5 seconds
                            if track_id == curr_obj["tracking_id"]:
                                start_time = prev_obj["start_time"]
                                delta_time = curr_time - start_time
                                # If object there for longer than 5 seconds trigger the flag and restart the start time
                                if delta_time >= 5:
                                    self.triggered = True
                                    curr_obj["start_time"] = curr_time

                                # Otherwise make the start_time of the previous frame the start time for this frame
                                else:
                                    curr_obj["start_time"] = start_time
                            else:
                                curr_obj["start_time"] = curr_time

            else:
                if curr_frame:
                    for curr_obj in curr_frame:
                        curr_obj["start_time"] = curr_time

            if curr_frame:
                previous_frame = curr_frame

            time.sleep(0.1)

    def stop(self):
        self.stopped = True
        time.sleep(2)
        self.device.stop()
        print("[INFO] Motion Capture Stopped")