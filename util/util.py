import cv2

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from collections import namedtuple
import numpy as np

Rectangle = namedtuple('Rectangle', 'x_min y_min x_max y_max')


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.6, thickness=1):
    """
    Draws a label with a box around it onto an image.
    :param image: the image to draw on
    :param point: the bottom left point of the bounding box containing the label
    :param label: the label which should be printed
    :param font: the font in which to draw the label (default: cv2.FONT_HERSHEY_SIMPLEX)
    :param font_scale: the scale with which to draw the label (default: 0.8)
    :param thickness: the thickness of the box around the label (default: 1)
    """
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (0, 0, 255), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


def draw_box(image, bbox):
    x_max = bbox[1][0]
    x_min = bbox[0][0]
    y_max = bbox[2][1]
    y_min = bbox[0][1]
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color=(0, 0, 255))


def draw_box_label(image, bbox, label, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.6, thickness=1):
    draw_box(image, bbox)
    draw_label(image, (bbox[0][0], bbox[0][1]), label, font, font_scale, thickness)


def draw_box_label_pillow(image, bbox, label, font=ImageFont.truetype("arial.ttf", 15), color='red', x_offset=0):
    x_min = int(bbox[0][0])
    y_min = int(bbox[0][1])

    # get text size
    text_size = font.getsize(label)

    # set button size + 10px margins
    button_size = (text_size[0]+10, text_size[1]+10)

    # create image with correct size and black background
    button_img = Image.new('RGBA', button_size, color)

    # put text on button with 10px margins
    button_draw = ImageDraw.Draw(button_img)
    button_draw.text((5, 5), label, font=font)

    # put button on source image in position (0, 0)
    image.paste(button_img, (x_min + x_offset, y_min - button_size[1]/2 if x_offset == 0 else y_min))

    return image


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def get_surface_area_polygon(x, y):
    """
    Calculate the surface area of a polygon
    :param x: the list of x-coordinates of each corner
    :param y: the list of y-coordinates of each corner
    :return: the surface area of the polygon
    """
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def get_overlapping_surface_area(a: Rectangle, b: Rectangle):
    """
    Returns the overlapping surface of 2 rectangles. Returns None if the rectangles are non-intersecting
    :param a: the first rectangle
    :param b: the second rectangle
    :return: the overlapping surface area of the 2 rectangles
    """
    dx = min(a.x_max, b.x_max) - max(a.x_min, b.x_min)
    dy = min(a.y_max, b.y_max) - max(a.y_min, b.y_min)
    if dx >= 0 and dy >= 0:
        return dx * dy
    else:
        return 0
