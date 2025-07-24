import cv2
import numpy as np

from typing import List

class CTillerCounter:
    def __init__(self) -> None:
        None
        
    @staticmethod
    def auto_detect_tillers_in_curr_img(path_image: str, param1: int = 95,
                                        param2: int =28, minRadius: int=14,
                                        maxRadius: int=40, MinDist: int=50) -> List:
        """
        Use Hough transform to find all tillers in image.

        Params:
            path_imgage (str): Filepath to the image
            param1 (int): param1 of cv2.HoughCircles(.) -> Higher threshold of Canny edge detector
            param2 (int): param2 of cv2.HoughCircles(.) -> Lower threshold of Canny edge detector
            minRadius (int): Minimum circle (i.e. tiller) radius
            maxRadius (int): Maximum circle (i.e. tiller) radius
            MinDist (int): Minimum distance between two tillers

        Returns:
            List of tillers
        """
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