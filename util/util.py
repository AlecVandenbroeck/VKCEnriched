import cv2

from PIL import Image, ImageFont, ImageDraw
from collections import namedtuple
import numpy as np
import math

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


def draw_box(image, bbox, thickness=1):
    x_max = bbox[1][0]
    x_min = bbox[0][0]
    y_max = bbox[2][1]
    y_min = bbox[0][1]
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color=(0, 0, 255), thickness=thickness)


def draw_box_label(image, bbox, label, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.6, thickness=1, box_thickness=1):
    draw_box(image, bbox, box_thickness)
    draw_label(image, (bbox[0][0], bbox[0][1]), label, font, font_scale, thickness)


def draw_box_label_pillow(image, bbox, label, text_size=None, font="arial.ttf", color='white', x_offset=0):
    x_min = int(bbox[0][0])
    y_min = int(bbox[0][1])
    y_max = int(bbox[2][1])

    # get text size
    font = ImageFont.truetype(font, text_size)
    font_text_size = font.getsize(label)

    # set button size + 10px margins
    button_size = (font_text_size[0]+6, font_text_size[1]+6)

    # create image with correct size and black background
    button_img = Image.new('RGBA', button_size, color)

    # put text on button with 10px margins
    button_draw = ImageDraw.Draw(button_img)
    button_draw.text((3, 3), label, font=font, fill='black')

    # put button on source image in position (0, 0)
    image.paste(button_img, (x_min + x_offset, y_min - button_size[1] if x_offset == 0 else y_min))

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


def segments_distance(x11, y11, x12, y12, x21, y21, x22, y22):
    """ distance between two segments in the plane:
      one segment is (x11, y11) to (x12, y12)
      the other is   (x21, y21) to (x22, y22)
    """
    if segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22):
        return 0
    # try each of the 4 vertices w/the other segment
    distances = [point_segment_distance(x11, y11, x21, y21, x22, y22),
                 point_segment_distance(x12, y12, x21, y21, x22, y22),
                 point_segment_distance(x21, y21, x11, y11, x12, y12),
                 point_segment_distance(x22, y22, x11, y11, x12, y12)]
    return min(distances)


def segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22):
    """ whether two segments in the plane intersect:
      one segment is (x11, y11) to (x12, y12)
      the other is   (x21, y21) to (x22, y22)
    """
    dx1 = x12 - x11
    dy1 = y12 - y11
    dx2 = x22 - x21
    dy2 = y22 - y21
    delta = dx2 * dy1 - dy2 * dx1
    if delta == 0:
        return False  # parallel segments
    s = (dx1 * (y21 - y11) + dy1 * (x11 - x21)) / delta
    t = (dx2 * (y11 - y21) + dy2 * (x21 - x11)) / (-delta)
    return (0 <= s <= 1) and (0 <= t <= 1)


def point_segment_distance(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:  # the segment's just a point
        return math.hypot(px - x1, py - y1)

    # Calculate the t that minimizes the distance.
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    # See if this represents one of the segment's
    # end points or a point in the middle.
    if t < 0:
        dx = px - x1
        dy = py - y1
    elif t > 1:
        dx = px - x2
        dy = py - y2
    else:
        near_x = x1 + t * dx
        near_y = y1 + t * dy
        dx = px - near_x
        dy = py - near_y

    return math.hypot(dx, dy)


def reskew_tesseract_output(extraction_output, image_deskewer):
    deskewed_extraction_output = []
    for i in extraction_output:
        top_left = [i['left'], i['top']]
        top_right = [i['left'] + i['width'], i['top']]
        bottom_left = [i['left'], i['top'] + i['height']]
        bottom_right = [i['left'] + i['width'], i['top'] + i['height']]
        top_left_deskewed = image_deskewer.inverse_transform_coords(np.array([[top_left]]))
        top_right_deskewed = image_deskewer.inverse_transform_coords(np.array([[top_right]]))
        bottom_left_deskewed = image_deskewer.inverse_transform_coords(np.array([[bottom_left]]))
        bottom_right_deskewed = image_deskewer.inverse_transform_coords(np.array([[bottom_right]]))
        i['left'] = int(min([top_left_deskewed[0][0][0], top_right_deskewed[0][0][0], bottom_left_deskewed[0][0][0], bottom_right_deskewed[0][0][0]]))
        i['top'] = int(min([top_left_deskewed[0][0][1], top_right_deskewed[0][0][1], bottom_left_deskewed[0][0][1], bottom_right_deskewed[0][0][1]]))
        i['width'] = int(max([top_left_deskewed[0][0][0], top_right_deskewed[0][0][0], bottom_left_deskewed[0][0][0], bottom_right_deskewed[0][0][0]]) - i['left'])
        i['height'] = int(max([top_left_deskewed[0][0][1], top_right_deskewed[0][0][1], bottom_left_deskewed[0][0][1], bottom_right_deskewed[0][0][1]]) - i['top'])
        deskewed_extraction_output.append(i)
    return deskewed_extraction_output


def line_intersects_text(img, p1, p2, text_bboxes):
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    x_upper = (-1/m)*p1[1] + p1[0]
    x_lower = (1/m)*(img.shape[1]-p1[1]) + p1[0]

    intersects = False
    for text_bbox in text_bboxes:
        si_1 = segments_intersect(x_upper, 0, x_lower, img.shape[1], text_bbox[0][0], text_bbox[0][1], text_bbox[1][0], text_bbox[1][1])
        si_2 = segments_intersect(x_upper, 0, x_lower, img.shape[1], text_bbox[1][0], text_bbox[1][1], text_bbox[2][0], text_bbox[2][1])
        si_3 = segments_intersect(x_upper, 0, x_lower, img.shape[1], text_bbox[2][0], text_bbox[2][1], text_bbox[3][0], text_bbox[3][1])
        si_4 = segments_intersect(x_upper, 0, x_lower, img.shape[1], text_bbox[3][0], text_bbox[3][1], text_bbox[0][0], text_bbox[0][1])
        if si_1 or si_2 or si_3 or si_4:
            intersects = True
            break

    return intersects
