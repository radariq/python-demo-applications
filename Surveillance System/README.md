## About
This program is a proof of concept application for 
use with the RadarIQ mmRadar module. The app 
demonstrates how you may utilize this module  
in conjunction with a camera to detect the movement
of a person in a defined area. 

Whenever an object is detected by the module, lingering
for 5 seconds or longer, the camera snaps a shot.
It uses a CNN (convolutional neural network) to determine 
if the captured image contains a person. If it does, 
the system saves the image for later viewing.

NOTE: This is designed to run on a Raspberry Pi.

To use, download all dependencies (***see requirements
notes***), run `python rpi_camera_surveillance_system.py` program, and point your browser to
```localhost:8000```.  Press the "Start Detection" 
button to start capturing. After you have stopped the 
detection, press the "Go To Detections" button to see 
the captured images. 

***Please note:*** 

This program is intended as a jumping board for 
your imagination. It does not have any security 
measures to assure privacy. Use discretion when
testing this system.

## Requirements
- [RadarIQ Python SDK](#)
- opencv_python 4.1.1
- imutils 0.5.3 +
- ***WARNING!!!*** if you are using a Raspberry Pi: 
to use all the features of opencv_python needed for 
this program you will need to compile from source. Thankfully,
the folks at [PyImageSearch](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/) 
have created a tutorial that offers complete instructions.
Follow ***all*** instructions including their version
of packages and pre-cleaning/maintenance instructions.

## Installation
1. Create a virtual env for this project

``python -m venv venv``

2. Activate the virtual env

* Windows: ``venv\scripts\activate``
* Linux: ``source venv/bin/activate``

3. Install requirements
``pip install -r requirements.txt``

OR:

Simply click on the "install" batch file and it will install
all the files required.

## License
Copyright 2021 RadarIQ, Ltd

Permission is hereby granted, free of charge, to 
any person obtaining a copy of this software and 
associated documentation files (the "Software"), 
to deal in the Software without restriction, 
including without limitation the rights to use, 
copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is 
furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice 
shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF 
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT 
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR 
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN 
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE 
OR OTHER DEALINGS IN THE SOFTWARE.