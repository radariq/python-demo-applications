People Counting
============================
Demonstration program counting people walking along a footpath etc.

This demonstration expects a person to walk in from either the left or the right of the sensors field of view
and walk out the other side. This works best when the person is about 5m away from the sensor.

There are two implementations provided here. One using the Point Cloud application and one using the Object Tracking application


Tips for usage:
1. Run this application once. This will set the relevant parameters on the sensor.
2. Open the RadarIQ Controller Application to visualise what the sensor is seeing. This will allow you to see the 
edges of the detection zone. Once you've done this close the RadarIQ Controller.
3. Run this application again and walk in and out of the areas you identified in step 2.

Usage:
------

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


4.Run the application
``python PeopleCountingObjectTracking.py``
``python PeopleCountingPointCloud.py``
```
-----------------------------------------
 \                                     /
  \                                   /          
   \                                 /
    \                               /
     \                             /
      \                           /
 <---- \          <----          /    <----Person
        \                       /
         \                     / 
          \                   /  
           --------------------
```