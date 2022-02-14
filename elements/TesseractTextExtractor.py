from PIL import Image
import pytesseract
from util import util


class TesseractTextExtractor:
    def __init__(self):
        pass

    def process(self, img) -> list:
        text_data = pytesseract.image_to_data(img, lang='fra', output_type=pytesseract.Output.DICT, config='--psm 6')
        text_dict = [
            dict(level=text_data['level'][x], page_num=text_data['page_num'][x], block_num=text_data['block_num'][x],
                 par_num=text_data['par_num'][x], line_num=text_data['line_num'][x], word_num=text_data['word_num'][x],
                 left=text_data['left'][x], top=text_data['top'][x], width=text_data['width'][x],
                 height=text_data['height'][x], conf=text_data['conf'][x], text=text_data['text'][x]) for x in
            range(len(text_data['block_num']))]
        return text_dict

    def visualize(self, img, text_dict):
        # Create image with whitespace on right side to print predictions
        annotated_img = Image.fromarray(img)
        padding = annotated_img.size[0]
        annotated_img = util.add_margin(annotated_img, 0, padding, 0, 0, (256, 256, 256))

        for prediction in text_dict:
            if prediction['text'] != '':
                x_max = prediction['left'] + prediction['width']
                x_min = prediction['left']
                y_max = prediction['top'] + prediction['height']
                y_min = prediction['top']
                annotated_img = util.draw_box_label_pillow(annotated_img,
                                                           [[x_min, y_min], [x_max, 0], [0, y_max], [0, 0]],
                                                           prediction['text'], color='green', x_offset=padding)

        return annotated_img

    def visualize_detections(self, img, text_dict: dict):
        for prediction in text_dict:
            x_max = prediction['left'] + prediction['width']
            x_min = prediction['left']
            y_max = prediction['top']
            y_min = prediction['top'] + prediction['height']
            util.draw_box(img, [[x_min, y_min], [x_max, 0], [0, y_max], [0, 0]])
        return img

    def to_alto(self, text_dict) -> str:
        alto_string = ""

        return
