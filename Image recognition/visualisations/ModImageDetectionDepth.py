# Image recognition code based on instructions from pyimagesearch.com

import cv2
import time
import imutils
import numpy as np
from imutils.video import VideoStream
from visualisations.VisualisationBase import VisualisationBase

np.set_printoptions(suppress=True)


class ModImageDetectionDepth(VisualisationBase):
    def __init__(self, data_getter, device):
        VisualisationBase.__init__(self, data_getter)
        # Image Recon Var
        self.cam_id = 0
        self.cam = None
        self.im1 = None
        self.PROTOTXT = None
        self.MODEL = None
        self.CONFIDENCE = None
        self.CLASSES = None
        self.COLORS = None
        self.net = None
        self.vs = None
        self.count = 0
        self.frame = None
        self.go = self.running
        self.viewport = 600

        # Start Image Recognition System
        self.start_image_recon()
        self.device = device
        print("[INFO] starting RadarIQ...")
        self.device.start()

    def show(self):
        """
        Loop for matching then displaying image detections and radar objects
        """
        print("[INFO] starting generator...")
        frame_generator = self.fetch_data()
        while self.go:
            # Capture radar frame
            frame = next(frame_generator)
            radar_frame = None

            # If a frame is available create a new frame with adjusted x_pos indexing
            if frame:
                radar_frame = self.adjust_x_pos(frame)

            # Capture image frame
            img_frame = self.vs.read()

            # Resize it to display width
            # TODO make the width a global variable
            img_frame = imutils.resize(img_frame, width=self.viewport)

            # Grab the frame dimensions and convert it to a blob
            (h, w) = img_frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(img_frame, (300, 300)),
                                         0.007843, (300, 300), 127.5)

            # Pass the blob through the self.network and obtain the detections and
            # predictions
            self.net.setInput(blob)
            detections = self.net.forward()

            # Transform np.array to a list, removes unused dimensions
            objects = detections[0,0].tolist()

            # Filter and organize detections that do not match person class in order of largest to smallest
            # TODO Make the filter class a global variable and pass it to this function
            objects = self.process_detections(objects)

            # Loop over the detections
            for i in range(len(objects)):

                # Determine the confidence level of the detected object
                confidence = objects[i][2]

                # Filter out weak detections and person objects by ensuring the `confidence` is
                if confidence > self.CONFIDENCE:

                    # Compute the (x, y)-coordinates of
                    # the bounding box for the object
                    box = objects[i][3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # Set local variable for handling object depth
                    depth = "N/A"
                    rad_obj = None

                    # Check if an object return from radar matches this detection
                    if radar_frame:
                        for obj in radar_frame:
                            if obj[0] in range(startX, endX):
                                depth = obj[1]["y_pos"]
                                rad_obj = obj

                    # Remove if a radar object has been assigned this detected object.
                    if rad_obj:
                        radar_frame.remove(rad_obj)

                    # Draw the prediction on the frame
                    label = "depth: {}".format(depth)
                    cv2.rectangle(img_frame, (startX, startY), (endX, endY),
                                  (255, 0, 0), 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(img_frame, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Display the result in its own window
            cv2.imshow("Press Esc To Exit", img_frame)
            key = cv2.waitKey(100)
            if key == 27:
                print("ESC")
                cv2.destroyAllWindows()
                break
            time.sleep(0.01)

    def start_image_recon(self):
        """
        Sets up and initializes the image recognition part of the application
        """
        # Image Recognition
        self.PROTOTXT = "assets/ssd_model/MobileNet-SSD-master/deploy.prototxt"
        self.MODEL = "assets/ssd_model/MobileNet-SSD-master/mobilenet_iter_73000.caffemodel"
        self.CONFIDENCE = 0.2

        # initialize the list of class labels MobileNet SSD was trained to
        # detect, then generate a set of bounding box colors for each class
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))

        print("[INFO] loading model...")
        self.net = cv2.dnn.readNetFromCaffe(self.PROTOTXT, self.MODEL)
        print("[INFO] starting video stream...")
        self.vs = VideoStream(src=0).start()
        self.cam = cv2.VideoCapture(self.cam_id)

    def adjust_x_pos(self, objects):
        """
        Takes a list of radar objects, calculates an adjusted x_pos based on ratio for each element,
        creates list of tuples with the adjusted x_pos, and original object,
        sorts the list of tuples from closes to farthest.
        """
        adj_x_list = []
        final_list = []
        for OBJECT in objects:
            original_x = OBJECT["x_pos"]
            y = abs(OBJECT["y_pos"])

            #  Scales x to be out of 400
            ratio = (y / self.viewport)
            new_x = original_x / ratio

            #  Adjust for center point variation
            new_x = 200 + round(new_x, 0)

            #  Add object to list indexed by adjusted x
            adj_x_list.append((new_x, OBJECT))

            #  Order the list so that the closest is first
            final_list = sorted(adj_x_list, key=lambda x: abs(x[1]["y_pos"]))
        return final_list

    def process_detections(self, obj_list):
        """
        Filters out detections that are not a person and organizes the list of objects from largest to smallest
        """
        # Filter out anything that is not a person i.e. self.CLASSES[15]
        obj_list = filter(lambda obj: obj[1] == 15.0, obj_list)

        # Return to list format
        obj_list = list(obj_list)

        # Sort by larger detections first  ((end_x - start_x) * 100) * ((end_y - start_y) * 100)
        final_list = sorted(obj_list, key=lambda x: ((x[4]-x[3])*100)*((x[6]-x[5])*100))

        return final_list
