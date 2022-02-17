import craft
import numpy as np
from util.util import segments_distance


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
        self.polys = None
        self.heatmap = None
        self.lines = None

    def process(self, img):
        # run the detector
        self.bboxes, self.polys, self.heatmap = craft.detect_text(img)
        return self.bboxes, self.polys, self.heatmap

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

    def get_line_bboxes(self, metric='euclidean'):
        if self.lines is None:
            self.lines = self.cluster_lines_friend(metric)
        self.lines_bboxes = []
        for i in self.lines:
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
            x_min = int(min(x_coords))
            x_max = int(max(x_coords))
            y_min = int(min(y_coords))
            y_max = int(max(y_coords))
            self.lines_bboxes.append([[x_min, y_min], [x_max, 0], [0, y_max], [0, 0]])
        return self.lines_bboxes

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

    def cluster_lines_friend(self, metric='euclidean', metric_scaling=3):
        # TODO: take into account if there is a vertical line between 2 words?
        lines = []
        centers = []
        for bbox in self.bboxes:
            centers.append(self.get_centers(bbox))

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

            lines.append([self.bboxes[most_left]])
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
                                               metric, metric_scaling) < lowest_dist and self.get_left_friend(centers,
                                                                                                              i) == most_left:
                                closest = i
                                lowest_dist = custom_distance(centers[most_left][1], centers[i][0], metric,
                                                              metric_scaling)
                if closest is not None:
                    _, h1 = self.get_dims(self.bboxes[most_left])
                    _, h2 = self.get_dims((self.bboxes[closest]))
                    threshold = (h1 + h2) * 3 / 2
                    print(f"{lowest_dist} / {threshold}")
                    if closest is not None and 0 <= lowest_dist <= threshold:
                        lines[len(lines) - 1].append(self.bboxes[closest])
                        used[closest] = True
                        most_left = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return lines

    def cluster_lines(self, bboxes):
        lines = []
        centers = []
        for bbox in bboxes:
            centers.append(self.get_centers(bbox))

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

            lines.append([bboxes[most_left]])
            used[most_left] = True
            keep_going = True
            while keep_going:
                lowest_dist = -1
                closest = None
                for i in range(len(centers)):
                    if not used[i]:
                        if closest is None:
                            closest = i
                            lowest_dist = custom_distance(centers[most_left][1], centers[i][0])
                        else:
                            if custom_distance(centers[most_left][1], centers[i][0]) < lowest_dist:
                                closest = i
                                lowest_dist = custom_distance(centers[most_left][1], centers[i][0])
                if closest is not None:
                    _, h1 = self.get_dims(bboxes[most_left])
                    _, h2 = self.get_dims((bboxes[closest]))
                    threshold = max([h1 + h2, 80])
                    if closest is not None and 0 <= lowest_dist <= threshold:
                        lines[len(lines) - 1].append(bboxes[closest])
                        used[closest] = True
                        most_left = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return lines

    def cluster_paragraphs(self, bboxes):
        blocks = []

        used = [False] * len(bboxes)
        outer_counter = 0
        while used != [True] * len(bboxes):
            outer_counter += 1
            most_top = None
            lowest_top = -1
            for i in range(len(bboxes)):
                if not used[i]:
                    if most_top is None:
                        most_top = i
                        lowest_top = bboxes[i][0][1]
                    else:
                        if bboxes[i][0][1] < lowest_top:
                            most_top = i
                            lowest_top = bboxes[i][0][1]

            blocks.append([bboxes[most_top]])
            used[most_top] = True
            keep_going = True
            while keep_going:
                lowest_dist = -1
                closest = None
                for i in range(len(bboxes)):
                    if not used[i]:
                        dist = segments_distance(bboxes[most_top][0][0], bboxes[most_top][2][1],
                                                 bboxes[most_top][1][0], bboxes[most_top][2][1],
                                                 bboxes[i][0][0], bboxes[i][0][1], bboxes[i][1][0],
                                                 bboxes[i][0][1])
                        if closest is None or dist < lowest_dist:
                            closest = i
                            lowest_dist = dist
                if closest is not None:
                    h1 = bboxes[most_top][2][1] - bboxes[most_top][0][1]
                    h2 = bboxes[closest][2][1] - bboxes[closest][0][1]
                    threshold = (h1 + h2) / 4
                    if closest is not None and 0 <= lowest_dist <= threshold:
                        blocks[len(blocks) - 1].append(bboxes[closest])
                        used[closest] = True
                        most_top = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return blocks

    def visualize(self, img, bboxes):
        img_boxed = craft.show_bounding_boxes(img, bboxes)

        return img_boxed
