import argparse
import os
import logging
import atexit
import laspy
import numpy as np
from radariq import RadarIQ, MODE_POINT_CLOUD, find_com_port

"""
Commandline tool for capturing point cloud data from the RadarIQ module into point cloud data formats

Usage Information: python capture.py --help
"""

logging.basicConfig(level=logging.ERROR)

riq = None  # RadarIQ Object instance

SPEED_UNITS = 'm/s'


def main(args):
    global riq

    try:
        atexit.register(exit_handler)
        setup_radariq(args)

        if args.start == 'C':  # Continuous
            riq.start()
        elif args.start == 'I':  # Interactive
            pass
        elif isinstance(args.start, int):  # Fixed number
            riq.start(args.start)

        count = 1

        if args.start == 'I':
            interactive(count)

        for frame in riq.get_data():
            if frame is not None:
                filename = build_filename(args.filename, args.format, count)
                if args.format == 'xyz':
                    formatted = xyz(frame)
                    write(formatted, filename)
                elif args.format == 'pcd':
                    formatted = pcd(frame)
                    write(formatted, filename)
                elif args.format == 'ply':
                    formatted = ply(frame)
                    write(formatted, filename)
                elif args.format == 'las':
                    las(frame, filename)

                count += 1
                if args.start == 'I':
                    interactive(count)
        exit_handler()
    except Exception as e:
        logging.error("Failed to get data from the RadarIQ module: {}".format(str(e)))
        exit(1)


def argparser():
    """
    Parse the commandline into a set of arguments.

    :return: Args
    """
    parser = argparse.ArgumentParser(description='RadarIQ Point Cloud Capture.')
    parser.add_argument('--filename', action='store', required=True, metavar="<filename>",
                        help='Filename to save the point cloud to.')
    parser.add_argument('--format', action='store', choices=['xyz', 'pcd', 'ply', 'las'], required=True,
                        help='The file format to export the point cloud as.')
    parser.add_argument('--port', action='store', metavar="<COM port>",
                        help='The COM port the RadarIQ module is connected to (eg. COM1). ' +
                             'If not specified the RadarIQ module will be automatically detected')
    parser.add_argument('--start', dest='start', type=validate_start, action='store', default='1',
                        help="The method of capturing frames. Each frame will be saved as a separate file (eg filename_1.xxx)"
                             "The number of frames to capture OR "
                             "'C' for continuous capture (press ctrl-C to stop), OR "
                             "'I' for interactive capture (prompt after each frame) or a fixed number of frames to capture."
                             " The default is to capture 1 frame")

    parser.add_argument('--units', action='store', default='m', choices=['mm', 'm', 'km', 'in', 'ft', 'mi'],
                        help='Distance units of measurement. Default is m')
    parser.add_argument('--distance-range', action='store', nargs=2, type=float, metavar=('min', 'max'),
                        help='Distance range.')
    parser.add_argument('--angle-range', action='store', nargs=2, type=float, metavar=('min', 'max'),
                        help='Viewing angle range.')
    parser.add_argument('--fps', action='store', default=2,
                        help='The frame rate to run the radar sensor at. Default is 2 fps')
    args = parser.parse_args()

    return args


def validate_start(value):
    """
    Validate function for the 'start' argument.

    :param value: Inputted value
     :type value: str
    :return: validated value
    """
    s_value = value.upper()
    if s_value in ['C', 'I']:
        return s_value
    elif int(value) >= 0:
        return int(value)
    else:
        raise argparse.ArgumentTypeError("%s is invalid. It must be 'I', 'C' or a positive integer" % value)


def setup_radariq(args):
    """
    Setup the RadarIQ module.

    :param args: The arguments from the command line
    :type args: Namespace
    """
    global riq

    if args.port is not None:
        port = args.port
    else:
        port = find_com_port().device

    riq = RadarIQ(port)
    riq.set_mode(MODE_POINT_CLOUD)
    riq.set_units(args.units, SPEED_UNITS)
    riq.set_frame_rate(args.fps)
    if args.distance_range is not None:
        riq.set_distance_filter(float(args.distance_range[0]), float(args.distance_range[1]))
    if args.angle_range is not None:
        riq.set_angle_filter(int(args.angle_range[0]), int(args.angle_range[1]))


def interactive(count):
    """
    Pause to get user input
    :param count:
    """
    riq.stop()
    input("Frame {}: Press [ENTER] to capture frame".format(count))
    riq.start(1)


def xyz(data):
    """
    Format the data into xyz format.

    :param data: Numpy array of points from the RadarIQ API.
    :type data: ndarray
    :return: Formatted string in xyz format.
    :rtype: str
    """
    output = 'X Y Z Intensity Velocity\n'
    for row in data:
        x = row[0]
        y = row[1]
        z = row[2]
        intensity = row[3]
        velocity = row[4]

        output += "{} {} {} {} {}\n".format(x, y, z, intensity, velocity)
    return output


def pcd(data):
    """
    Format the data into pcd format.
    See: http://pointclouds.org/documentation/tutorials/pcd_file_format.php

    :param data: Numpy array of points from the RadarIQ API.
    :type data: ndarray
    :return: Formatted string in xyz format.
    :rtype: str
    """

    output = ''
    count = 0
    for row in data:
        x = row[0]
        y = row[1]
        z = row[2]
        intensity = row[3]
        velocity = row[4]
        count += 1
        output += "{} {} {} {} {}\n".format(x, y, z, intensity, velocity)

    header = (
            "# .PCD v.7 - Point Cloud Data file format\n" +
            "VERSION .7\n" +
            "FIELDS x y z intensity velocity\n" +
            "SIZE 4 4 4 4 4\n" +
            "TYPE F F F F F\n" +
            "COUNT 1 1 1 1 1\n" +
            "WIDTH 1\n" +
            "HEIGHT 1\n" +
            "VIEWPOINT 0 0 0 1 0 0 0\n" +
            "POINTS {}\n".format(count) +
            "DATA ascii\n"
    )

    return header + output


def ply(data):
    """
    Format the data into ply format.
    https://www.mathworks.com/help/vision/ug/the-ply-format.html

    :param data: Numpy array of points from the RadarIQ API.
    :type data: ndarray
    :return: Formatted string in ply format.
    :rtype: str
    """
    output = ''
    count = 0
    for row in data:
        x = row[0]
        y = row[1]
        z = row[2]
        intensity = row[3]
        velocity = row[4]
        count += 1
        output += "{} {} {} {} {}\n".format(x, y, z, intensity, velocity)

    header = ("ply\n" +
              "format ascii 1.0\n" +
              "element vertex {}\n".format(count) +
              "property float x\n" +
              "property float y\n" +
              "property float z\n" +
              "property float intensity\n" +
              "property float velocity\n" +
              "end_header\n")
    return header + output


def las(data, filename):
    """
    Format the data into las format.

    :param data: Numpy array of points from the RadarIQ API.
    :type data: ndarray
    :param filename Filename to save to.
    :type filename: str
    :return: Formatted string in las format.
    :rtype: str
    """
    all_x, all_y, all_z, all_intensities = _prepare_las(data)

    x_min = np.floor(np.min(all_x))
    y_min = np.floor(np.min(all_y))
    z_min = np.floor(np.min(all_z))

    x_max = np.ceil(np.max(all_x))
    y_max = np.ceil(np.max(all_y))
    z_max = np.ceil(np.max(all_z))

    hdr = laspy.header.Header()
    outfile = laspy.file.File(filename, mode="w", header=hdr)
    outfile.header.min = [x_min, y_min, z_min]
    outfile.header.max = [x_max, y_max, z_max]
    outfile.header.offset = [x_min, y_min, z_min]
    outfile.header.software_id = 'RadarIQ LAS Capture'.zfill(32)
    outfile.header.scale = [0.001, 0.001, 0.001]  # @todo work out what this should be
    outfile.x = all_x
    outfile.y = all_y
    outfile.z = all_z
    outfile.intensity = all_intensities
    outfile.close()

    return outfile


def _prepare_las(data):
    """
    Prepares data into a las-compatible format.

    :param data: Numpy array of points from the RadarIQ API.
    :type data: ndarray
    :return: Formatted x,y,z,intensities, velocity.
    :rtype: Tuple[ndarray, ndarray, ndarray, ndarray, ndarray]
    """

    swapped = np.swapaxes(data, 0, 1)
    all_x = np.array([])
    all_y = np.array([])
    all_z = np.array([])
    all_intensities = np.array([])
    all_velocities = np.array([])

    all_x = np.concatenate((all_x, np.array(swapped[0])))
    all_y = np.concatenate((all_y, np.array(swapped[1])))
    all_z = np.concatenate((all_z, np.array(swapped[2])))
    all_intensities = np.concatenate((all_intensities, np.array(swapped[3])))
    all_velocities = np.concatenate((all_velocities, np.array(swapped[4])))

    return all_x, all_y, all_z, all_intensities, all_velocities


def write(formatted, filename):
    """
    Write the formatted data to a file.

    :param formatted: Formatted data.
    :type formatted: str
    :param filename: Name of the file to save to.
    :type filename: str
    """

    try:
        mode = 'w+'
        f = open(filename, mode)
        f.write(formatted)
        f.close()
    except Exception as e:
        logging.error("Failed to write to file: " + str(e))
        exit(1)


def build_filename(filename, ext, count):
    """
    Builds the filename based on the selected arguments.

    :param filename: The filename.
    :type: filename: str
    :param ext: The extension
    :type ext: str
    :param count: The current frame number.
    :type count: int
    :return: Fully formatted filename
    :rtype: str
    """

    # Ensure extension
    if filename[-4:] != '.' + ext:
        filename += '.' + ext

    # Add frame counter if not a single frame capture
    filename, file_extension = os.path.splitext(filename)
    return "{}_{:03d}{}".format(filename, count, file_extension)


def exit_handler():
    """
    Catch the program exiting (ctrl C)
    """
    global riq
    try:
        riq.close()
    except Exception as err:
        logging.error(err)
        pass


if __name__ == '__main__':
    args = argparser()
    main(args)
