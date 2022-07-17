# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
import time
import io
from os import walk
from pathlib import Path
import socketserver
from threading import Condition
import threading
from http import server
from detect_motion import DetectMotion
from detect_person import DetectPerson
from image_system import ImageSystem

INDEX_PAGE = """\
<html>
<head>
<title>RadarIQ Motion Surveillance- Disabled</title>
<style>
        body {
            background: #0033A0;
            color: white;
            font-family: Arial, Helvetica, sans-serif;
        }
        button {
            background-color: white;
            border: none;
            color: black;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 25px
        }
</style>
</head>
<body>
<center><h1>RadarIQ Motion Surveillance- Disabled</h1></center>
<center><button type="submit" onclick="location.href='/on'">Start Surveillance</button></center>
<center><button type="submit" onclick="location.href='/detections'">Go To Detections</button></center>
</body>
</html>
"""

ON_PAGE = """\
<html>
<head>
<title>RadarIQ Motion Surveillance- Enabled</title>
    <style>
        body {
            background: #0033A0;
            color: white;
            font-family: Arial, Helvetica, sans-serif;
          }
        button {
            background-color: white;
            border: none;
            color: black;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 25px
            }
    </style>
</head>
<body>
<center><h1>RadarIQ Motion Surveillance- Enabled</h1></center>
<center><button type="submit" onclick="location.href='/index.html'">Stop Surveillance</button></center>

</body>
</html>
"""

# Motion detection helper classes initialized
detecting = False

dm = DetectMotion()
dp = DetectPerson()
img_sys = ImageSystem()

# captures current path for relative path applications
save_path = str(Path.cwd())


def start_detection():
    global detecting
    detecting = True
    # Thread to detect movement from the RadarIQ module
    detect_thread = threading.Thread(target=dm.start)
    detect_thread.start()
    while detecting:
        # Check if attribute triggered has changed for helper class
        if dm.triggered:
            # Capture a single image frame from the connected camera
            frame = img_sys.capture()
            # Detect if there is a person on the frame and save the image if there is
            if dp.detect(frame):
                img_sys.save(frame)
            # Change variable to its untriggeredd state.
            dm.triggered = False
        # Sleep to allow detect_tread to run of needed
        time.sleep(0.1)


def stop_detection():
    global detecting
    # Change detecting to false to exit while loop in start_detection function.
    detecting = False
    # Stop the RadarIQ module
    dm.stop()


# Server request handler
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            stop_detection()
            content = INDEX_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/on':
            content = ON_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            start_detection()
        elif self.path == '/detections':
            content = self.create_gallery()
            content = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        # Handle PNG Images
        elif "png" in self.path:
            try:
                with open(self.path, 'rb') as img:
                    content = img.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
            except:
                self.send_error(404)
                self.end_headers()

        else:
            self.send_error(404)
            self.end_headers()

    # Dynamically creates an html page to display the captured images
    def create_gallery(self, kind="list"):
        # HTML string constant elements
        HEAD = """\
        <html>
        <head>
            <title>RadarIQ Motion Surveillance- Gallery</title>
            <style>
                body {
                    background: #0033A0;
                    color: white;
                    font-family: Arial, Helvetica, sans-serif;
                  }
                button {
                    background-color: white;
                    border: none;
                    color: black;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 25px;
                    }
            </style>
        </head>
        """
        BODY_TOP = """\
        <body>
        <center><h1>RadarIQ Motion Surveillance- Gallery</h1></center>
        <center><button type="submit" onclick="location.href='/detections'">Refresh</button></center>
        <center><table style="width:40%; border: 1px solid black; background-color: #ffffff">
        
        """

        BODY_BOTTOM = """\
                    </center>
                </table>
            </body>
        </html>
        """

        # Creates a files list and populates it with the names of the files contained on the /detected folder
        files = []
        for (dirpath, dirnames, filenames) in walk(save_path +"/detected"):
            files.extend(filenames)

        # HTML string started
        html_str = HEAD + BODY_TOP

        # Create a link to each file and labels it with the date and time of capture.
        for file in files:
            date, hour = file.split("+")
            date = date[6:]
            date = date.replace("-", "/")
            hour = hour[:11]
            hour = hour.replace("_", ":")
            if kind is "list":
                html_str += f"<tr><td><a href='{save_path}/detected/{file}'>Captured {date} at {hour}.</a></td></tr>"

        # HTML string concluded
        html_str += BODY_BOTTOM

        return html_str


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


# Initialize server system
address = ('', 8000)
server = StreamingServer(address, StreamingHandler)
server.serve_forever()