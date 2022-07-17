import os
import logging
import numpy as np
from threading import Thread
from time import time

from radariq.RadarIQ import RadarIQ, MODE_POINT_CLOUD, OUTPUT_NUMPY
from radariq import port_manager as pm

try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    import tkinter as tk
    from tkinter import messagebox

try:
    import ttk
    py3 = False

except ImportError:
    import tkinter.ttk as ttk
    py3 = True

"""
Example program which takes a measurement of an object using statistical methods
"""
# Initialize Window
window = tk.Tk()

# Constants
FRAME_RATE = 5  # frames per second
CAPTURE_LENGTH = 5  # Number of seconds to capture for


# Variables
min_distance = tk.StringVar()  # Minimum distance to search and set default
min_distance.set("10.0")
max_distance = tk.StringVar()  # Maximum distance to search
max_distance.set("2000.0")
min_angle = tk.StringVar()  # Minimum angle to search
min_angle.set("-30")
max_angle = tk.StringVar()  # Maximum angle to search
max_angle.set("30")
min_height = tk.StringVar()  # Minimum height to search
min_height.set("-5000")
max_height = tk.StringVar()  # Maximum height to search
max_height.set("5000")
com_port = tk.StringVar(None)  # COM PORT device is connected
connected = False  # Connection Status of Device
rad_iq = None
cap_data = 0

# Logging
FORMAT = '%(asctime)-15s %(message)'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('RadarIQ')
logger.setLevel(logging.INFO)


def auto_detect():
    """
    Uses the port_manager app to detect the COM port of any connected RadarIQ devices.
    """
    global rad_iq, connected, com_port
    try:
        com_ports = pm.find_com_ports()
        connection_port = str(com_ports[0])[:4]
        rad_iq = RadarIQ(connection_port, output_format=OUTPUT_NUMPY)
        connected = True
        com_port.set(connection_port)

    except Exception as error:
        py_ver_message("Connection Error", str(error), False)
        return False


def bar_and_capture():
    """
    Displays pop-up while measurement is taken.
    """
    global p_value, rad_iq
    cap_thread = Thread(target=capture)
    p_frame.deiconify()

    # @TODO Create a helper function that updates the location of application window
    l_progressbar.place(relx=0.5, rely=0.33, anchor=tk.CENTER)
    l_progressbar.configure(text="Taking Readings:")
    p_progressbar.place(relx=0.5, rely=0.66, anchor=tk.CENTER)
    cap_thread.start()
    p_progressbar.start(10)
    while cap_thread.is_alive():
        p_frame.update()
    p_frame.withdraw()


def calculate_distance(data):
    """
    Processes the points data to find average and standard deviation
    """
    average = float(np.mean(data))
    stdev = float(np.std(data))
    return average, stdev


def capture():
    """
    Captures distance data using RadarIQ object based on the parameters gathered from the UI.
    """
    global rad_iq, cap_data
    riq_obj = rad_iq
    try:
        riq_obj.stop()
        riq_obj.set_mode(MODE_POINT_CLOUD)
        riq_obj.set_units('mm', 'mm/s')
        riq_obj.set_frame_rate(FRAME_RATE)
        riq_obj.set_distance_filter(float(min_distance.get()), float(max_distance.get()))
        riq_obj.set_angle_filter(int(min_angle.get()), int(max_angle.get()))
        riq_obj.set_height_filter(float(min_height.get()), float(max_height.get()))
        riq_obj.start(FRAME_RATE * CAPTURE_LENGTH)

        all_ys = np.empty(shape=[0, 1])

        for frame in riq_obj.get_data():
            print(frame)
            if frame is not None:

                ys = frame[:, 1]  # y's
                print(ys)
                all_ys = np.append(all_ys, ys)

        print("Successfully captured.")

        cap_data = all_ys

    except Exception as error:
        print(error)


def connect_riq():
    """
    Connects program to RadarIQ device and returns a RadarIQ object.
    """
    global rad_iq, connected, com_port
    try:

        if com_port.get() != "":
            rad_iq = RadarIQ(com_port.get())
            connected = True
            return True

        else:
            return auto_detect()

    except Exception as error:
        print(error)
        return False


def display_distance(average, stdev):
    """
    Updates the display of distance and accuracy
    """
    round_average = round(average, 0)
    round_stdev = round(stdev, 0)
    l_display_distance.configure(text="{} mm".format(round_average))
    l_display_distance.update()
    l_accuracy.configure(text="Accuracy: {} mm +/-".format(round_stdev))
    l_accuracy.update()


def measure():
    global rad_iq
    if not connected:
        connect_riq()
    if connected:
        bar_and_capture()
        average, stdev = calculate_distance(cap_data)
        display_distance(average, stdev)


def py_ver_message(title, message, ask):
    """
    Displays messages according to python version.
    """
    if py3:
        if ask:
            return messagebox.askokcancel(title, message, parent=window)
        else:
            messagebox.showerror(title, message, parent=window)
    else:
        if ask:
            return tkMessageBox.askokcancel(title, message, parent=window)
        else:
            tkMessageBox.showerror(title, message, parent=window)


def shut_down():
    """
    Closes the program and disconnects from the device.
    """
    if py_ver_message("Exit", "Are you sure you want to exit?", True):
        if rad_iq is not None:
            rad_iq.close()
        window.destroy()


def validate_distance_func(p):
    """
    Validate that a distance number is valid (can convert to a int)

    If it is not, then a ValueError is thrown
    :param p: The number to convert
    """
    try:
        if p == '':
            return True

        v = float(p)

        # Get max distance (10m) in relevant units

        if 0 <= v <= 10000.0:
            return True
        else:
            return False
    except ValueError:
        return False


def validate_height_func(p):
    """
        Validate that a height number is valid (can convert to a int)

        If it is not, then a ValueError is thrown
        :param p: The number to convert
    """
    try:
        if p == '' or p == '-':
            return True

        v = float(p)

        # Get max distance (10m) in relevant units

        if -5000 <= v <= 5000:
            return True
        else:
            return False
    except ValueError:
        return False


def validate_angle_func(p):
    """
    Validate that a angle number is valid (can convert to a int)

    If it is not, then a ValueError is thrown
    :param p: The number to convert
    """
    try:
        print('p', p)
        if p == '' or p == '-':
            return True

        v = int(p)
        if -60 <= v <= 60:
            return True
        else:
            return False

    except ValueError:
        return False


#################################################################
# GUI Config
#################################################################

# ======================================================
# Modified by Rozen to remove Tkinter import statements and to receive
# the font as an argument.
# ======================================================
# Found the original code at:
# http://code.activestate.com/recipes/576688-tooltip-for-tkinter/
# ======================================================


class ToolTip(tk.Toplevel):
    """
    Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor
    """

    def __init__(self, wdgt, tooltip_font, msg=None, msgFunc=None,
                 delay=1, follow=True):
        """
        Initialize the ToolTip

        Arguments:
          wdgt: The widget this ToolTip is assigned to
          tooltip_font: Font to be used
          msg:  A static string message assigned to the ToolTip
          msgFunc: A function that retrieves a string to use as the ToolTip text
          delay:   The delay in seconds before the ToolTip appears(may be float)
          follow:  If True, the ToolTip follows motion, otherwise hides
        """
        self.wdgt = wdgt
        # The parent of the ToolTip is the parent of the ToolTips widget
        self.parent = self.wdgt.master
        # Initalise the Toplevel
        tk.Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        # Hide initially
        self.withdraw()
        # The ToolTip Toplevel should have no frame or title bar
        self.overrideredirect(True)

        # The msgVar will contain the text displayed by the ToolTip
        self.msgVar = tk.StringVar()
        if msg is None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(msg)
        self.msgFunc = msgFunc
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        # The text of the ToolTip is displayed in a Message widget
        tk.Message(self, textvariable=self.msgVar, bg='#FFFFDD',
                   font=tooltip_font,
                   aspect=1000).grid()

        # Add bindings to the widget.  This will NOT override
        # bindings that the widget already has
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        """
        Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget

        Arguments:
          event: The event that called this funciton
        """
        self.visible = 1
        # The after function takes a time argument in miliseconds
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        """
        Displays the ToolTip if the time delay has been long enough
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """
        Processes motion within the widget.
        Arguments:
          event: The event that called this function
        """

        self.lastMotion = time()
        # If the follow flag is not set, motion within the
        # widget will make the ToolTip disappear
        #
        if self.follow is False:
            self.withdraw()
            self.visible = 1

        # Offset the ToolTip 10x10 pixes southwest of the pointer
        self.geometry('+%i+%i' % (event.x_root + 20, event.y_root - 10))
        try:
            # Try to call the message function.  Will not change
            # the message if the message function is None or
            # the message function fails
            self.msgVar.set(self.msgFunc())
        except:
            pass
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """
        Hides the ToolTip.  Usually this is caused by leaving the widget
        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()


# ===========================================================
#                   End of Class ToolTip
# ===========================================================

# Main Window
window.title("Radar IQ Distance Demo")
window.geometry("350x519+100+100")
window.minsize(350, 519)
window.maxsize(4804, 1400)
window.resizable(1, 1)
window.configure(background="#ffffff")
window.configure(highlightbackground="#d9d9d9")
window.configure(highlightcolor="black")

photo = tk.PhotoImage(file=os.path.relpath('assets/logo_sm.gif'))
window.iconbitmap(os.path.relpath("assets/favicon.ico"))
l_logo = tk.Label(window, image=photo, background="#ffffff")
l_logo.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# Center Measurement
measurement_frame = tk.Frame(window)
measurement_frame.place(relx=0.05, rely=0.17, relheight=0.30, relwidth=0.90)
measurement_frame.configure(background="#ffffff")

l_display_distance = tk.Label(measurement_frame)
l_display_distance.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
l_display_distance.configure(activebackground="#f9f9f9")
l_display_distance.configure(activeforeground="black")
l_display_distance.configure(background="#ffffff")
l_display_distance.configure(disabledforeground="#a3a3a3")
l_display_distance.configure(foreground="#000000")
l_display_distance.configure(highlightbackground="#d9d9d9")
l_display_distance.configure(highlightcolor="black")
l_display_distance.configure(text='''N/A''')
l_display_distance.configure(font="none 40 bold")

l_accuracy = tk.Label(measurement_frame)
l_accuracy.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
l_accuracy.configure(activebackground="#f9f9f9")
l_accuracy.configure(activeforeground="black")
l_accuracy.configure(background="#ffffff")
l_accuracy.configure(disabledforeground="#a3a3a3")
l_accuracy.configure(foreground="#000000")
l_accuracy.configure(highlightbackground="#d9d9d9")
l_accuracy.configure(highlightcolor="black")
l_accuracy.configure(text='''(Accuracy: X mm +/-)''')
l_accuracy.configure(font="none 10 bold")

# Settings Area
l_f_settings = tk.LabelFrame(window)
l_f_settings.place(relx=0.05, rely=0.50, relheight=0.29,
                   relwidth=0.9)
l_f_settings.configure(relief='groove')
l_f_settings.configure(foreground="black")
l_f_settings.configure(text='''Settings''')
l_f_settings.configure(background="#ffffff")
l_f_settings.configure(highlightbackground="#d9d9d9")
l_f_settings.configure(highlightcolor="black")

tooltip_font = "TkDefaultFont"

# Max/Min Labels
l_minimum = tk.Label(l_f_settings)
l_minimum.place(relx=0.269, rely=0.10, height=26, width=69
                , bordermode='ignore')
l_minimum.configure(activebackground="#f9f9f9")
l_minimum.configure(activeforeground="black")
l_minimum.configure(background="#ffffff")
l_minimum.configure(disabledforeground="#a3a3a3")
l_minimum.configure(foreground="#000000")
l_minimum.configure(highlightbackground="#d9d9d9")
l_minimum.configure(highlightcolor="black")
l_minimum.configure(text='''Minimum''')

l_maximum = tk.Label(l_f_settings)
l_maximum.place(relx=0.603, rely=0.10, height=26, width=72
                , bordermode='ignore')
l_maximum.configure(activebackground="#f9f9f9")
l_maximum.configure(activeforeground="black")
l_maximum.configure(background="#ffffff")
l_maximum.configure(disabledforeground="#a3a3a3")
l_maximum.configure(foreground="#000000")
l_maximum.configure(highlightbackground="#d9d9d9")
l_maximum.configure(highlightcolor="black")
l_maximum.configure(text='''Maximum''')

# Distance Filter Row
l_distance = tk.Label(l_f_settings)
l_distance.place(relx=0.034, rely=0.225, height=26, width=63
                 , bordermode='ignore')
l_distance.configure(activebackground="#f9f9f9")
l_distance.configure(activeforeground="black")
l_distance.configure(anchor='ne')
l_distance.configure(background="#ffffff")
l_distance.configure(disabledforeground="#a3a3a3")
l_distance.configure(foreground="#000000")
l_distance.configure(highlightbackground="#d9d9d9")
l_distance.configure(highlightcolor="black")
l_distance.configure(text='''Distance''')

e_filter_distance_min = tk.Entry(l_f_settings)
e_filter_distance_min.place(relx=0.276, rely=0.24, height=20
                            , relwidth=0.221, bordermode='ignore')
e_filter_distance_min.configure(background="white")
e_filter_distance_min.configure(disabledforeground="#a3a3a3")
e_filter_distance_min.configure(font="TkFixedFont")
e_filter_distance_min.configure(foreground="#000000")
e_filter_distance_min.configure(highlightbackground="#d9d9d9")
e_filter_distance_min.configure(highlightcolor="black")
e_filter_distance_min.configure(insertbackground="black")
e_filter_distance_min.configure(selectbackground="#c4c4c4")
e_filter_distance_min.configure(selectforeground="black")
e_filter_distance_min.configure(textvariable=min_distance)
e_filter_distance_min.configure(validate="all")
validate_distance = e_filter_distance_min.register(validate_distance_func)
e_filter_distance_min.configure(validatecommand=((validate_distance, '%P')))
ToolTip(e_filter_distance_min, tooltip_font, '''Must be between 0 and 10000 millimeters''', delay=0.5)

l_to_distance = tk.Label(l_f_settings)
l_to_distance.place(relx=0.517, rely=0.225, height=26, width=20
                    , bordermode='ignore')
l_to_distance.configure(activebackground="#f9f9f9")
l_to_distance.configure(activeforeground="black")
l_to_distance.configure(background="#ffffff")
l_to_distance.configure(disabledforeground="#a3a3a3")
l_to_distance.configure(foreground="#000000")
l_to_distance.configure(highlightbackground="#d9d9d9")
l_to_distance.configure(highlightcolor="black")
l_to_distance.configure(text='''to''')

e_filter_distance_max = tk.Entry(l_f_settings)
e_filter_distance_max.place(relx=0.621, rely=0.24, height=20
                            , relwidth=0.221, bordermode='ignore')
e_filter_distance_max.configure(background="white")
e_filter_distance_max.configure(disabledforeground="#a3a3a3")
e_filter_distance_max.configure(font="TkFixedFont")
e_filter_distance_max.configure(foreground="#000000")
e_filter_distance_max.configure(highlightbackground="#d9d9d9")
e_filter_distance_max.configure(highlightcolor="black")
e_filter_distance_max.configure(insertbackground="black")
e_filter_distance_max.configure(selectbackground="#c4c4c4")
e_filter_distance_max.configure(selectforeground="black")
e_filter_distance_max.configure(textvariable=max_distance)
e_filter_distance_max.configure(validate="all")
validate_distance = e_filter_distance_max.register(validate_distance_func)
e_filter_distance_max.configure(validatecommand=(validate_distance, '%P'))
ToolTip(e_filter_distance_max, tooltip_font,'''Must be between 0 and 10000 millimeters''', delay=0.5)

l_distance_filter_units = tk.Label(l_f_settings)
l_distance_filter_units.place(relx=0.862, rely=0.225, height=26
                              , width=32, bordermode='ignore')
l_distance_filter_units.configure(activebackground="#f9f9f9")
l_distance_filter_units.configure(activeforeground="black")
l_distance_filter_units.configure(anchor='w')
l_distance_filter_units.configure(background="#ffffff")
l_distance_filter_units.configure(disabledforeground="#a3a3a3")
l_distance_filter_units.configure(foreground="#000000")
l_distance_filter_units.configure(highlightbackground="#d9d9d9")
l_distance_filter_units.configure(highlightcolor="black")
l_distance_filter_units.configure(text='''mm''')

# Angle Filter Row
l_angle = tk.Label(l_f_settings)
l_angle.place(relx=0.069, rely=0.365, height=31, width=51
              , bordermode='ignore')
l_angle.configure(activebackground="#f9f9f9")
l_angle.configure(activeforeground="black")
l_angle.configure(anchor='ne')
l_angle.configure(background="#ffffff")
l_angle.configure(disabledforeground="#a3a3a3")
l_angle.configure(foreground="#000000")
l_angle.configure(highlightbackground="#d9d9d9")
l_angle.configure(highlightcolor="black")
l_angle.configure(text='''Angle''')

e_filter_angle_min = tk.Entry(l_f_settings)
e_filter_angle_min.place(relx=0.276, rely=0.37, height=20
                         , relwidth=0.221, bordermode='ignore')
e_filter_angle_min.configure(background="white")
e_filter_angle_min.configure(disabledforeground="#a3a3a3")
e_filter_angle_min.configure(font="TkFixedFont")
e_filter_angle_min.configure(foreground="#000000")
e_filter_angle_min.configure(highlightbackground="#d9d9d9")
e_filter_angle_min.configure(highlightcolor="black")
e_filter_angle_min.configure(insertbackground="black")
e_filter_angle_min.configure(selectbackground="#c4c4c4")
e_filter_angle_min.configure(selectforeground="black")
e_filter_angle_min.configure(textvariable=min_angle)
e_filter_angle_min.configure(validate="all")
validate_angle = e_filter_angle_min.register(validate_angle_func)
e_filter_angle_min.configure(validatecommand=((validate_angle, '%P')))
ToolTip(e_filter_angle_min, tooltip_font, '''Must be between -60 and 60 degrees''', delay=0.5)

l_to_angle = tk.Label(l_f_settings)
l_to_angle.place(relx=0.517, rely=0.365, height=21, width=17
                 , bordermode='ignore')
l_to_angle.configure(activebackground="#f9f9f9")
l_to_angle.configure(activeforeground="black")
l_to_angle.configure(background="#ffffff")
l_to_angle.configure(disabledforeground="#a3a3a3")
l_to_angle.configure(foreground="#000000")
l_to_angle.configure(highlightbackground="#d9d9d9")
l_to_angle.configure(highlightcolor="black")
l_to_angle.configure(text='''to''')

e_filter_angle_max = tk.Entry(l_f_settings)
e_filter_angle_max.place(relx=0.621, rely=0.37, height=20
                         , relwidth=0.221, bordermode='ignore')
e_filter_angle_max.configure(background="white")
e_filter_angle_max.configure(disabledforeground="#a3a3a3")
e_filter_angle_max.configure(font="TkFixedFont")
e_filter_angle_max.configure(foreground="#000000")
e_filter_angle_max.configure(highlightbackground="#d9d9d9")
e_filter_angle_max.configure(highlightcolor="black")
e_filter_angle_max.configure(insertbackground="black")
e_filter_angle_max.configure(selectbackground="#c4c4c4")
e_filter_angle_max.configure(selectforeground="black")
e_filter_angle_max.configure(textvariable=max_angle)
e_filter_angle_max.configure(validate="all")
validate_angle = e_filter_angle_max.register(validate_angle_func)
e_filter_angle_max.configure(validatecommand=((validate_angle, '%P')))
ToolTip(e_filter_angle_max, tooltip_font, '''Must be between -60 and 60 degrees''', delay=0.5)

l_angle_units = tk.Label(l_f_settings)
l_angle_units.place(relx=0.862, rely=0.365, height=20, width=28
                    , bordermode='ignore')
l_angle_units.configure(activebackground="#f9f9f9")
l_angle_units.configure(activeforeground="black")
l_angle_units.configure(anchor='w')
l_angle_units.configure(background="#ffffff")
l_angle_units.configure(disabledforeground="#a3a3a3")
l_angle_units.configure(foreground="#000000")
l_angle_units.configure(highlightbackground="#d9d9d9")
l_angle_units.configure(highlightcolor="black")
l_angle_units.configure(text='''deg''')

# Height Filter Row
l_height = tk.Label(l_f_settings)
l_height.place(relx=0.069, rely=0.495, height=31, width=51
               , bordermode='ignore')
l_height.configure(activebackground="#f9f9f9")
l_height.configure(activeforeground="black")
l_height.configure(anchor='ne')
l_height.configure(background="#ffffff")
l_height.configure(disabledforeground="#a3a3a3")
l_height.configure(foreground="#000000")
l_height.configure(highlightbackground="#d9d9d9")
l_height.configure(highlightcolor="black")
l_height.configure(text='''Height''')

e_filter_height_min = tk.Entry(l_f_settings)
e_filter_height_min.place(relx=0.276, rely=0.50, height=20
                          , relwidth=0.221, bordermode='ignore')
e_filter_height_min.configure(background="white")
e_filter_height_min.configure(disabledforeground="#a3a3a3")
e_filter_height_min.configure(font="TkFixedFont")
e_filter_height_min.configure(foreground="#000000")
e_filter_height_min.configure(highlightbackground="#d9d9d9")
e_filter_height_min.configure(highlightcolor="black")
e_filter_height_min.configure(insertbackground="black")
e_filter_height_min.configure(selectbackground="#c4c4c4")
e_filter_height_min.configure(selectforeground="black")
e_filter_height_min.configure(textvariable=min_height)
e_filter_height_min.configure(validate="all")
validate_height = e_filter_height_min.register(validate_height_func)
e_filter_height_min.configure(validatecommand=((validate_height, '%P')))
tooltip_font = "TkDefaultFont"
ToolTip(e_filter_height_min, tooltip_font, '''Must be between -5000 and 5000''', delay=0.5)

l_to_height = tk.Label(l_f_settings)
l_to_height.place(relx=0.517, rely=0.495, height=21, width=17
                  , bordermode='ignore')
l_to_height.configure(activebackground="#f9f9f9")
l_to_height.configure(activeforeground="black")
l_to_height.configure(background="#ffffff")
l_to_height.configure(disabledforeground="#a3a3a3")
l_to_height.configure(foreground="#000000")
l_to_height.configure(highlightbackground="#d9d9d9")
l_to_height.configure(highlightcolor="black")
l_to_height.configure(text='''to''')

e_filter_height_max = tk.Entry(l_f_settings)
e_filter_height_max.place(relx=0.621, rely=0.50, height=20
                          , relwidth=0.221, bordermode='ignore')
e_filter_height_max.configure(background="white")
e_filter_height_max.configure(disabledforeground="#a3a3a3")
e_filter_height_max.configure(font="TkFixedFont")
e_filter_height_max.configure(foreground="#000000")
e_filter_height_max.configure(highlightbackground="#d9d9d9")
e_filter_height_max.configure(highlightcolor="black")
e_filter_height_max.configure(insertbackground="black")
e_filter_height_max.configure(selectbackground="#c4c4c4")
e_filter_height_max.configure(selectforeground="black")
e_filter_height_max.configure(textvariable=max_height)
e_filter_height_max.configure(validate="all")
validate_height = e_filter_height_max.register(validate_height_func)
e_filter_height_max.configure(validatecommand=((validate_height, '%P')))
tooltip_font = "TkDefaultFont"
ToolTip(e_filter_height_max, tooltip_font, '''Must be between -5000 and 5000''', delay=0.5)

l_height_filter_units = tk.Label(l_f_settings)
l_height_filter_units.place(relx=0.862, rely=0.495, height=26
                            , width=32, bordermode='ignore')
l_height_filter_units.configure(activebackground="#f9f9f9")
l_height_filter_units.configure(activeforeground="black")
l_height_filter_units.configure(anchor='w')
l_height_filter_units.configure(background="#ffffff")
l_height_filter_units.configure(disabledforeground="#a3a3a3")
l_height_filter_units.configure(foreground="#000000")
l_height_filter_units.configure(highlightbackground="#d9d9d9")
l_height_filter_units.configure(highlightcolor="black")
l_height_filter_units.configure(text='''mm''')

# COM Port Settings Row
l_com_port = tk.Label(l_f_settings)
l_com_port.place(relx=0.29, rely=0.705, height=21, width=63
                 , bordermode='ignore', anchor=tk.CENTER)
l_com_port.configure(activebackground="#f9f9f9")
l_com_port.configure(activeforeground="black")
l_com_port.configure(background="#ffffff")
l_com_port.configure(disabledforeground="#a3a3a3")
l_com_port.configure(foreground="#000000")
l_com_port.configure(highlightbackground="#d9d9d9")
l_com_port.configure(highlightcolor="black")
l_com_port.configure(text='''COM Port''')

e_com_port = tk.Entry(l_f_settings)
e_com_port.place(relx=0.50, rely=0.705, height=20
                 , relwidth=0.221, bordermode='ignore', anchor=tk.CENTER)
e_com_port.configure(background="white")
e_com_port.configure(disabledforeground="#a3a3a3")
e_com_port.configure(font="TkFixedFont")
e_com_port.configure(foreground="#000000")
e_com_port.configure(highlightbackground="#d9d9d9")
e_com_port.configure(highlightcolor="black")
e_com_port.configure(insertbackground="black")
e_com_port.configure(selectbackground="#c4c4c4")
e_com_port.configure(selectforeground="black")
e_com_port.configure(textvariable=com_port)

b_com_port = tk.Button(l_f_settings)
b_com_port.place(relx=0.73, rely=0.68, height=20,
                 relwidth=0.2, anchor=tk.CENTER)
b_com_port.configure(activebackground="#ececec")
b_com_port.configure(activeforeground="#000000")
b_com_port.configure(background="#0033a0")
b_com_port.configure(command=auto_detect)
b_com_port.configure(disabledforeground="#a3a3a3")
b_com_port.configure(font="-family {Segoe UI} -size 8")
b_com_port.configure(foreground="#ffffff")
b_com_port.configure(highlightbackground="#d9d9d9")
b_com_port.configure(highlightcolor="black")
b_com_port.configure(text='''Detect''')

# Capture Button
b_start = tk.Button(window)
b_start.place(relx=0.05, rely=0.85, relheight=0.10,
              relwidth=0.9)
b_start.configure(activebackground="#ececec")
b_start.configure(activeforeground="#ffffff")
b_start.configure(background="#ba0c2f")
b_start.configure(command=measure)
b_start.configure(disabledforeground="#a3a3a3")
b_start.configure(font="-family {Segoe UI} -size 13")
b_start.configure(foreground="#ffffff")
b_start.configure(highlightbackground="#d9d9d9")
b_start.configure(highlightcolor="black")
b_start.configure(pady="0")
b_start.configure(text='''Measure''')

# Progress Pop Up
p_interval = 100 / CAPTURE_LENGTH
p_value = 0

p_frame = tk.Toplevel(window)
p_frame_width = int(window.winfo_width()/1.5)
p_frame_height = 100
p_frame_x = int(window.winfo_x() + ((window.winfo_width()/2) - (p_frame_width/2)))
p_frame_y = int(window.winfo_y() + (window.winfo_height()/2) - (p_frame_height/2))
p_frame.geometry("{}x{}+{}+{}".format(p_frame_width, p_frame_height, p_frame_x, p_frame_y))
p_frame.configure(background="#ffffff")
p_frame.configure(highlightbackground="#d9d9d9")
p_frame.configure(highlightcolor="black")
p_frame.title("Capture")
p_frame.iconbitmap(os.path.relpath("assets/favicon.ico"))

l_progressbar = tk.Label(p_frame)
l_progressbar.place(relx=0.5, rely=0.33, anchor=tk.CENTER)
l_progressbar.configure(activebackground="#f9f9f9")
l_progressbar.configure(activeforeground="black")
l_progressbar.configure(background="#ffffff")
l_progressbar.configure(disabledforeground="#a3a3a3")
l_progressbar.configure(foreground="#000000")
l_progressbar.configure(highlightbackground="#d9d9d9")
l_progressbar.configure(highlightcolor="black")
l_progressbar.configure(text="Taking Readings:")

# @TODO Match bar coloring to rest of the app
p_progressbar = ttk.Progressbar(p_frame)
p_progressbar.place(relx=0.5, rely=0.66, anchor=tk.CENTER)


p_frame.withdraw()


#################################################################
# End GUI Config
#################################################################

if __name__ == '__main__':
    window.wm_protocol("WM_DELETE_WINDOW", shut_down)
    window.mainloop()
