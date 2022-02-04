from util.util import Rectangle, get_overlapping_surface_area


class CraftFilter:
    def process(self, extraction_output, craft_lines):
        cleaned_extraction_output = []
        for i in extraction_output:
            total_overlap = 0
            r1 = Rectangle(i['left'], i['top'], i['left'] + i['width'], i['top'] + i['height'])
            for j in craft_lines:
                x_min = j[0][0]
                x_max = j[1][0]
                y_min = j[0][1]
                y_max = j[2][1]
                r2 = Rectangle(x_min, y_min, x_max, y_max)
                overlap = get_overlapping_surface_area(r1, r2)
                if overlap is not None:
                    total_overlap += get_overlapping_surface_area(r1, r2)
            percentage_overlap = total_overlap / get_overlapping_surface_area(r1, r1)
            if percentage_overlap >= 0.7:
                cleaned_extraction_output.append(i)

        return cleaned_extraction_output
