import craft
import numpy as np


def custom_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + 8 * (p1[1] - p2[1]) ** 2)


class CraftDetector:
    def process(self, img):
        # run the detector
        bboxes, polys, heatmap = craft.detect_text(img)

        return bboxes, polys, heatmap

    def get_centers(self, bbox):
        y_min = min([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        y_max = max([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        x_min = min([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        x_max = max([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        left_center = (int(x_min), int(y_min + (y_max - y_min) / 2))
        right_center = (int(x_max), int(y_min + (y_max - y_min) / 2))
        return [left_center, right_center]

    def get_dims(self, bbox):
        y_min = min([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        y_max = max([bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]])
        x_min = min([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        x_max = max([bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        return x_max-x_min, y_max-y_min


    def get_line_bboxes(self, lines):
        lines_bboxes = []
        for i in lines:
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
            lines_bboxes.append([[x_min, y_min], [x_max, 0], [0, y_max], [0, 0]])
        return lines_bboxes

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
                    threshold = h1+h2
                    if closest is not None and 0 <= lowest_dist <= threshold:
                        lines[len(lines) - 1].append(bboxes[closest])
                        used[closest] = True
                        most_left = closest
                    else:
                        keep_going = False
                else:
                    keep_going = False

        return lines

    def visualize(self, img, bboxes):
        img_boxed = craft.show_bounding_boxes(img, bboxes)

        return img_boxed
