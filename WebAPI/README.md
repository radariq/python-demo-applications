Web API Bridge
============================

This script provides a basic bridge between the RadarIQ SDK and a websocket connection.

This will enable the module to use used in a web environment, and also across a network.

![Screenshot](demo.png).

Usage:
------


1. Create a virtual env for this project
    ``python -m venv venv``

2. Activate the virtual env

    * Windows: ``venv\scripts\activate``
    * Linux: ``source venv/bin/activate``

3. Install requirements

    ``pip install -r requirements.txt``

4. Run the application

    ``python main.py``

5. Open a web browser and navigate to
    ``http://localhost:8080``

API
===

The socketIO API tightly wraps the Python SDK.

There are three things to understand:

**Sending a command**

``
socket.emit('command', {"method":"<method name>"});
``

OR

``
socket.emit('command', {"method":"<method name>", "args":[<args>]});
``

where ``<method name>`` is the name of a method from the RadarIQ SDK and
``args`` is an optional array of parameters to feed to the method.

**Listening for messages**

A message can be:
* A message received by the RadarIQ Sensor itself
* A log message created by the Python SDK
* An exception thrown by the API Bridge

This is a simple example::

      socket.on('message', function(msg){
        console.log('[LOG]', msg)
      });

**Listening for data**

Any data produced by the ``get_data`` method will be available by listening to the ``data`` event::

    socket.on('data', function(data){
        console.log('[Data]', data)
    });

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

