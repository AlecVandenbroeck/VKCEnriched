class LTRBConverter:
    def process(self, extraction_output, output_path):
        with open(output_path, 'w+') as text_file:
            for i in extraction_output:
                if i['text'] != '':
                    ltrb_str = f'''{i['left']}, {i['top']}, {i['left'] + i['width']}, {i['top'] + i['height']}, "{i['text']}"\n'''
                    text_file.write(ltrb_str)