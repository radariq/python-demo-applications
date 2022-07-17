import threading

from tkinter import *
from visualisations.ModObjectPlot2D import ModObjectPlot2D
from radariq.RadarIQ import RadarIQ, MODE_OBJECT_TRACKING, OUTPUT_LIST
from visualisations.ModImageDetectionDepth import ModImageDetectionDepth

# RadarIQ module variable
sleep = 0.2
sensitivity = 5

# RadarIQ setting for initialization
settings = {
    'distance_units': "mm",
    'speed_units': "m/s",
    'acceleration_units': "mm/s²",
    'distance_min': 0.0,
    'distance_max': 6000.0,
    'angle_min': -55,
    'angle_max': 55,
    'height_min': -1000.00,
    'height_max': 1000.00,
    'frame_rate': 20,
}

# RadarIQ module initialization
device = RadarIQ(output_format=OUTPUT_LIST, sleep=sleep)
device.stop()
device.connection.flush_all()

device.stop()
device.set_mode(MODE_OBJECT_TRACKING)
device.set_units('mm', 'mm/s')
device.set_frame_rate(settings['frame_rate'])
device.set_distance_filter(settings['distance_min'], settings['distance_max'])
device.set_angle_filter(settings['angle_min'], settings['angle_max'])
device.set_height_filter(settings['height_min'], settings['height_max'])
device.set_sensitivity(sensitivity)

# Visualization initializations
data = device.get_data

vis_img_depth = ModImageDetectionDepth(data, device)
vis_obj_plot = ModObjectPlot2D(data, settings, device)

# Display initializations
img_thread = threading.Thread(target=vis_img_depth.show)

img_thread.start()
vis_obj_plot.show()



def exit_test():
    vis_img_depth.stop()
    vis_obj_plot.stop()
    device.stop()
    device.close()
    sys.exit()

# Exit system
exit_test()
