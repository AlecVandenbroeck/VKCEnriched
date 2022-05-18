import cv2
import numpy as np
from statistics import mean
from util.util import *


class PageSplitter:
    def process(self, img, par_bboxes):
        # Use canny edge detection
        edges = cv2.Canny(img, 50, 150, apertureSize=3)

        # Apply HoughLinesP method to
        # to directly obtain line end points
        lines = cv2.HoughLinesP(
            edges,  # Input edge image
            1,  # Distance resolution in pixels
            np.pi / 720,  # Angle resolution in radians
            threshold=75,  # Min number of votes for valid line
            minLineLength=50,  # Min allowed length of line
            maxLineGap=20  # Max allowed gap between line for joining them
        )

        lines_list = []
        x_list = []
        # Iterate over points
        for points in lines:
            x1, y1, x2, y2 = points[0]
            # Extracted points nested in the list
            angle = np.arctan2([x2 - x1], [y2 - y1]) / np.pi * 180
            if (170 < angle or 10 > angle) and not line_intersects_text(img, [x1, y1], [x2, y2], par_bboxes):
                x_list.append(x1)
                x_list.append(x2)
                # Maintain a simples lookup list for points
                lines_list.append([(x1, y1), (x2, y2)])

        x_mean = mean(x_list)
        return x_mean, lines
