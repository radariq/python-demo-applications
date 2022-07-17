import cv2
from imutils.video import VideoStream
import datetime
from pathlib import Path

save_path = str(Path.cwd())


class ImageSystem:
    def __init__(self):
        self.vs = VideoStream(src=0).start()

    def capture(self):
        img = self.vs.read()
        return img

    def save(self, frame):
        # cv2.imshow("test", frame)
        # cv2.waitKey(0)
        curr_time = datetime.datetime.now().strftime("%d-%m-%y+%I_%M_%S_%p")
        file_path = save_path + "/detected/detect" + curr_time + ".png"
        cv2.imwrite(file_path, frame)


