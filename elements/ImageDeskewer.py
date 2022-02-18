import math
from typing import Tuple, Union

import cv2
import numpy as np

from deskew import determine_skew


def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2

    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


class ImageDeskewer:
    def __init__(self):
        self.angle = None
        self.angle_radian = None
        self.rotation_matrix = None
        self.original_height = None
        self.original_width = None
        self.new_height = None
        self.new_width = None
        self.center = None
        self.initialized = False

    def fit(self, img: np.ndarray) -> None:
        grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.angle = determine_skew(grayscale, num_angles=4500, num_peaks=50)
        self.original_width, self.original_height = img.shape[:2]
        self.angle_radian = math.radians(self.angle)
        self.new_width = abs(np.sin(self.angle_radian) * self.original_height) + abs(np.cos(self.angle_radian) * self.original_width)
        self.new_height = abs(np.sin(self.angle_radian) * self.original_width) + abs(np.cos(self.angle_radian) * self.original_height)
        self.center = tuple(np.array(img.shape[1::-1]) / 2)
        self.rotation_matrix = cv2.getRotationMatrix2D(self.center, self.angle, 1.0)
        self.rotation_matrix[1, 2] += (self.new_width - self.original_width) / 2
        self.rotation_matrix[0, 2] += (self.new_height - self.original_height) / 2
        self.initialized = True
        return

    def transform(self, image: np.ndarray) -> Union[np.ndarray, None]:
        if self.initialized:
            return cv2.warpAffine(image, self.rotation_matrix, (int(round(self.new_height)),
                                                                int(round(self.new_width))), borderValue=(0, 0, 0))
        else:
            print("ImageDeskewer has to be initialized using the fit function before calling transform")
            return None

    def inverse_transform_coords(self, coords):
        inverse_rotation_matrix = cv2.getRotationMatrix2D(self.center, -self.angle, 1.0)
        inverse_rotation_matrix[1, 2] += (self.new_width - self.original_width) / 2
        inverse_rotation_matrix[0, 2] += (self.new_height - self.original_height) / 2
        rotated_coords = cv2.transform(coords, inverse_rotation_matrix)
        rotated_coords[0] = rotated_coords[0] - (self.new_width - self.original_width)
        rotated_coords[1] = rotated_coords[1] - (self.new_height - self.original_height)
        return rotated_coords
