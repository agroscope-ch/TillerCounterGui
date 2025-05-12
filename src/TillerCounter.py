import cv2
import numpy as np


class CTillerCounter:
    def __init__(self) -> None:
        None
        
    @staticmethod
    def auto_detect_tillers_in_curr_img(path_image: str, param1: int = 95, 
                                        param2: int =28, minRadius: int=14, 
                                        maxRadius: int=40, MinDist: int=50) -> np.ndarray:
        """ Use Hough transform to find all tillers in image. """
        img_orig = cv2.imread(path_image, cv2.IMREAD_COLOR)
        img      = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
        img      = cv2.medianBlur(img, 5)
        circles  = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, minDist=MinDist,
                                                param1=param1, param2=param2,
                                                minRadius=minRadius, maxRadius=maxRadius)
        tillers_curr_img_list = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                radius = i[2]
                tillers_curr_img_list.append([center, radius])
        
        return tillers_curr_img_list