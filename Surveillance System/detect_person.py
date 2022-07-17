import cv2
import imutils


class DetectPerson:
    def __init__(self):
        self.viewport = 400

        # Image Recognition
        self.PROTOTXT = "assets/ssd_model/MobileNet-SSD-master/deploy.prototxt"
        self.MODEL = "assets/ssd_model/MobileNet-SSD-master/mobilenet_iter_73000.caffemodel"
        self.CONFIDENCE = 0.2

        print("[INFO] loading model...")
        self.net = cv2.dnn.readNetFromCaffe(self.PROTOTXT, self.MODEL)

    def detect(self, frame):
        # Resize frame for faster detection
        img_frame = imutils.resize(frame, width=self.viewport)

        # Create blob to feed to the neural net
        blob = cv2.dnn.blobFromImage(cv2.resize(img_frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # Blob provided to neural net
        self.net.setInput(blob)

        # Neural network activated
        detections = self.net.forward()

        # Removes unnecessary data from the detection and return only objects information
        obj_list = detections[0, 0].tolist()

        # Removes objects that are not a person
        obj_list = filter(lambda obj: obj[1] == 15.0, obj_list)

        # Turn the the filter iterable object into a list
        obj_list = list(obj_list)

        # Notify if any person where detected on the frame
        if obj_list:
            return True

        else:
            return False
