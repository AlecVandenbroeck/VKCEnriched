import craft
import numpy as np
from util.util import segments_distance
from util.util import Rectangle
from util.util import get_overlapping_surface_area
from util.decorators import TimeLogger


def custom_distance(p1, p2, metric='euclidean', metric_scaling=3):
    if metric == 'manhattan':
        return abs(p1[0] - p2[0]) + metric_scaling * abs(p1[1] - p2[1])
    else:
        return np.sqrt((p1[0] - p2[0]) ** 2 + metric_scaling ** 2 * (p1[1] - p2[1]) ** 2)


class CraftDetector:
    def __init__(self):
        self.bboxes = None
        self.lines_bboxes = None
        self.par_bboxes = None
        self.lines = None
        self.paragraphs = None
        self.dims = None

    @TimeLogger
    def process(self, img):
        self.dims = img.shape[:2]
        # run the detector
        self.bboxes = craft.detect_text(img)
        return self.bboxes

    @staticmethod
    def get_extremes(bbox):
        y_min = min([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        y_max = max([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        x_min = min([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        x_max = max([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        return x_min, y_min, x_max, y_max

    def get_centers(self, bbox):
        x_min, y_min, x_max, y_max = self.get_extremes(bbox)
        left_center = (int(x_min), int(y_min + (y_max - y_min) / 2))
        right_center = (int(x_max), int(y_min + (y_max - y_min) / 2))
        return [left_center, right_center]

    def get_dims(self, bbox):
        x_min, y_min, x_max, y_max = self.get_extremes(bbox)
        return x_max - x_min, y_max - y_min

    def transform_to_bboxes(self, input_arr):
        res = []
        for i in input_arr:
            x_coords = []
            y_coords = []
            for j in i:
                x_coords.append(j[0][0])
                x_coords.append(j[1][0])
                x_coords.append(j[2][0])
                x_coords.append(j[3][0])
                y_coords.append(j[0][1])
                y_coords.append(j[1][1])
                y_coords.append(j[2][1])
                y_coords.append(j[3][1])
            x_min = int(max([0, min(x_coords)]))
            x_max = int(min([self.dims[1], max(x_coords)]))
            y_min = int(max([0, min(y_coords)]))
            y_max = int(min([self.dims[0], max(y_coords)]))
            res.append([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]])
        return res

    def get_line_bboxes(self):
        if self.lines is None:
            self.lines = self.cluster_lines_friend()
        self.lines_bboxes = self.transform_to_bboxes(self.lines)
        self.lines_bboxes = self.nms(self.lines_bboxes)
        return self.lines_bboxes

    def get_par_bboxes(self):
        if self.paragraphs is None:
            self.paragraphs = self.cluster_paragraphs()
        self.par_bboxes = self.transform_to_bboxes(self.paragraphs)
        self.par_bboxes = self.nms(self.par_bboxes)
        return self.par_bboxes

    @staticmethod
    def get_right_friend(centers, i):
        lowest_distance = -1
        closest_index = None
        right = centers[i][1]
        for j in range(len(centers)):
            if i == j:
                continue
            left = centers[j][0]
            distance = custom_distance(left, right)
            if closest_index is None or lowest_distance > distance:
                lowest_distance = distance
                closest_index = j
        return closest_index

    @staticmethod
    def get_left_friend(centers, i):
        lowest_distance = -1
        closest_index = None
        left = centers[i][0]
        for j in range(len(centers)):
            if i == j:
                continue
            right = centers[j][1]
            distance = custom_distance(left, right)
            if closest_index is None or lowest_distance > distance:
                lowest_distance = distance
                closest_index = j
        return closest_index

    @TimeLogger
    def cluster_lines_friend(self, metric='euclidean', metric_scaling=3):
        # TODO: take into account if there is a vertical line between 2 words?
        self.lines = []
        centers = []
        for bbox in self.bboxes:
            centers.append(self.get_centers(bbox))

        left_friends = []
        for c in range(len(centers)):
            left_friends.append(self.get_left_friend(centers, c))

        used = [False] * len(centers)
        outer_counter = 0
        while used != [True] * len(centers):
            outer_counter += 1
            most_left = None
            lowest_left = -1
            for i in range(len(centers)):
                if not used[i]:
                    if most_left is None:
                        most_left = i
                        lowest_left = centers[i][0][0]
                    else:
                        if centers[i][0][0] < lowest_left:
                            most_left = i
                            lowest_left = centers[i][0][0]

            self.lines.append([self.bboxes[most_left]])
            used[most_left] = True
            keep_going = True
            while keep_going:
                lowest_dist = -1
                closest = None
                for i in range(len(centers)):
                    if not used[i]:
                        if closest is None:
                            closest = i
                            lowest_dist = custom_distance(centers[most_left][1], centers[i][0], metric, metric_scaling)
                        else:
                            if custom_distance(centers[most_left][1], centers[i][0],
                                               metric, metric_scaling) < lowest_dist and left_friends[i] == most_left:
                                closest = i
                                lowest_dist = custom_distance(centers[most_left][1], centers[i][0], metric,
                                                              metric_scaling)
                if closest is not None:
                    _, h1 = self.get_dims(self.bboxes[most_left])
                    _, h2 = self.get_dims((self.bboxes[closest]))
                    threshold = (h1 + h2)
                    if closest is not None and 0 <= lowest_dist <= threshold:
                        self.lines[len(self.lines) - 1].append(self.bboxes[closest])
                        used[closest] = True
                        most_left = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return self.lines

    # def cluster_lines(self, bboxes):
    #     self.lines = []
    #     centers = []
    #     for bbox in bboxes:
    #         centers.append(self.get_centers(bbox))
    #
    #     used = [False] * len(centers)
    #     outer_counter = 0
    #     while used != [True] * len(centers):
    #         outer_counter += 1
    #         most_left = None
    #         lowest_left = -1
    #         for i in range(len(centers)):
    #             if not used[i]:
    #                 if most_left is None:
    #                     most_left = i
    #                     lowest_left = centers[i][0][0]
    #                 else:
    #                     if centers[i][0][0] < lowest_left:
    #                         most_left = i
    #                         lowest_left = centers[i][0][0]
    #
    #         lines.append([bboxes[most_left]])
    #         used[most_left] = True
    #         keep_going = True
    #         while keep_going:
    #             lowest_dist = -1
    #             closest = None
    #             for i in range(len(centers)):
    #                 if not used[i]:
    #                     if closest is None:
    #                         closest = i
    #                         lowest_dist = custom_distance(centers[most_left][1], centers[i][0])
    #                     else:
    #                         if custom_distance(centers[most_left][1], centers[i][0]) < lowest_dist:
    #                             closest = i
    #                             lowest_dist = custom_distance(centers[most_left][1], centers[i][0])
    #             if closest is not None:
    #                 _, h1 = self.get_dims(bboxes[most_left])
    #                 _, h2 = self.get_dims((bboxes[closest]))
    #                 threshold = max([h1 + h2, 80])
    #                 if closest is not None and 0 <= lowest_dist <= threshold:
    #                     lines[len(lines) - 1].append(bboxes[closest])
    #                     used[closest] = True
    #                     most_left = closest
    #                 else:
    #                     keep_going = False
    #             else:
    #                 keep_going = False
    #
    #     return lines

    @TimeLogger
    def cluster_paragraphs(self):
        if self.lines_bboxes is None:
            self.get_line_bboxes()

        self.paragraphs = []

        used = [False] * len(self.lines_bboxes)
        outer_counter = 0
        while used != [True] * len(self.lines_bboxes):
            outer_counter += 1
            most_top = None
            lowest_top = -1
            for i in range(len(self.lines_bboxes)):
                if not used[i]:
                    if most_top is None:
                        most_top = i
                        lowest_top = self.lines_bboxes[i][0][1]
                    else:
                        if self.lines_bboxes[i][0][1] < lowest_top:
                            most_top = i
                            lowest_top = self.lines_bboxes[i][0][1]

            self.paragraphs.append([self.lines_bboxes[most_top]])
            used[most_top] = True
            keep_going = True
            while keep_going:
                lowest_dist = -1
                closest = None
                for i in range(len(self.lines_bboxes)):
                    if not used[i]:
                        dist = segments_distance(self.lines_bboxes[most_top][0][0], self.lines_bboxes[most_top][2][1],
                                                 self.lines_bboxes[most_top][1][0], self.lines_bboxes[most_top][2][1],
                                                 self.lines_bboxes[i][0][0], self.lines_bboxes[i][0][1],
                                                 self.lines_bboxes[i][1][0], self.lines_bboxes[i][0][1])
                        if closest is None or dist < lowest_dist:
                            closest = i
                            lowest_dist = dist
                if closest is not None:
                    h1 = self.lines_bboxes[most_top][2][1] - self.lines_bboxes[most_top][0][1]
                    h2 = self.lines_bboxes[closest][2][1] - self.lines_bboxes[closest][0][1]
                    threshold = (h1 + h2) / 4
                    if closest is not None and 0 <= lowest_dist <= threshold and h2*1/2 <= h1 <= h2*2:
                        self.paragraphs[len(self.paragraphs) - 1].append(self.lines_bboxes[closest])
                        used[closest] = True
                        most_top = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return self.paragraphs

    @staticmethod
    def visualize(img, bboxes):
        img_boxed = craft.show_bounding_boxes(img, bboxes)

        return img_boxed

    @staticmethod
    def nms(bboxes, overlap_threshold=0.75):
        filtered_bboxes = []
        for i in range(len(bboxes)):
            should_stay = True
            a = Rectangle(bboxes[i][0][0], bboxes[i][0][1], bboxes[i][1][0], bboxes[i][2][1])
            surface = get_overlapping_surface_area(a, a)
            for j in range(len(bboxes)):
                if i != j:
                    b = Rectangle(bboxes[j][0][0], bboxes[j][0][1], bboxes[j][1][0], bboxes[j][2][1])
                    overlap = get_overlapping_surface_area(a, b) / surface
                    if overlap > overlap_threshold:
                        should_stay = False
                        break
            if should_stay:
                filtered_bboxes.append(bboxes[i])
        return filtered_bboxes
