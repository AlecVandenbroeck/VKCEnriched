from pytorch_ocr import main
from PIL import Image
from util.util import add_margin, draw_box_label_pillow


class PTTextExtractor:
    def __init__(self, craft_path: str, ocr_model_path: str, refiner_model_path: str):
        self.extractor = main.PytorchTextExtractor(craft_path, ocr_model_path, refiner_model_path, use_gpu=True,
                                                   write_debug=False)

    def process(self, img, bboxes, spell_checker=None):
        output = []

        for bbox in bboxes:
            # Get min and max for both x and y axis
            x_max = int(bbox[1][0])
            x_min = int(bbox[0][0])
            y_max = int(bbox[2][1] + 6)
            y_min = int(bbox[0][1] - 6)

            # Make text predictions
            text_predictions = self.extractor.process_frame(img[y_min:y_max, x_min:x_max])

            # If no text predicted, add NULL entry in the output
            if len(text_predictions) == 0:
                output.append(dict(word="NULL", bounding_box=bbox, corrected=False))

            else:
                for text_prediction in text_predictions:
                    word = text_prediction[1]

                    # If a spellingchecker was given as argument, use it
                    if spell_checker is not None:
                        misspelled = spell_checker.unknown([word])
                        if len(misspelled) > 0:
                            word = spell_checker.correction(word)

                    output.append(dict(word=word, bounding_box=bbox, corrected=(word != text_prediction[1])))

        return output

    def visualize(self, img, output):
        # Create image with whitespace on right side to print predictions
        annotated_img = Image.fromarray(img)
        padding = annotated_img.size[0]
        annotated_img = add_margin(annotated_img, 0, padding, 0, 0, (256, 256, 256))

        for prediction in output:
            x_max = int(prediction['bounding_box'][1][0])
            x_min = int(prediction['bounding_box'][0][0])
            y_max = int(prediction['bounding_box'][2][1] + 6)
            y_min = int(prediction['bounding_box'][0][1] - 6)
            annotated_img = draw_box_label_pillow(annotated_img, prediction['bounding_box'], prediction['word'],
                                                  color='green' if not prediction['corrected'] else 'blue',
                                                  x_offset=padding)

        return annotated_img
