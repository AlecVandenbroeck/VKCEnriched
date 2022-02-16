class HocrConverter:
    def __init__(self):
        self.started_line = False
        self.started_par = False
        self.started_block = False
        self.started_page = False
        self.page_count = 0
        self.block_count = 0
        self.par_count = 0
        self.line_count = 0
        self.word_count = 0
        self.tab_count = 0
        self._hocr_str = None

    def add_closing_tags(self, level):
        if self.started_page and level < 2:
            self.tab_count -= 1
            self.add_to_str("""<\div>""")
            self.started_page = False
        if self.started_block and level < 3:
            self.tab_count -= 1
            self.add_to_str("""<\div>""")
            self.started_block = False
        if self.started_par and level < 4:
            self.tab_count -= 1
            self.add_to_str("""<\p>""")
            self.started_par = False
        if self.started_line and level < 5:
            self.tab_count -= 1
            self.add_to_str("""<\span>""")
            self.started_line = False

    def add_first_tags(self):
        self.add_to_str("""<?xml version="1.0" encoding="UTF-8"?>""")
        self.add_to_str("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""")
        self.add_to_str("""<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">""")
        self.tab_count += 1
        self.add_to_str("""<head>""")
        self.tab_count += 1
        self.add_to_str("""<title></title>""")
        self.add_to_str("""<meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>""")
        self.add_to_str("""<meta name='ocr-system' content='tesseract 5.0.1-9-g31a968' />""")
        self.add_to_str(
            """<meta name='ocr-capabilities' content='ocr_page ocr_carea ocr_par ocr_line ocrx_word ocrp_wconf'/>""")
        self.tab_count -= 1
        self.add_to_str("""</head>""")
        self.add_to_str("""<body>""")
        self.tab_count += 1

    def add_final_tags(self):
        self.tab_count -= 1
        self.add_to_str("""</body>""")
        self.tab_count -= 1
        self.add_to_str("""</html>""")

    def add_to_str(self, input_str: str):
        if self._hocr_str is None:
            self._hocr_str = input_str
        else:
            self._hocr_str += '\n' + ' ' * self.tab_count + input_str

    def process(self, data_input) -> str:
        self._hocr_str = None
        self.add_first_tags()
        for i in data_input:
            self.add_closing_tags(i['level'])
            if i['level'] == 1:
                self.page_count += 1
                self.add_to_str(
                    f"""<div class='ocr_page' id='page_{self.page_count}' title='image "/content/dataset/1852/00009.png"; bbox {i['left']} {i['top']} {i['left'] + i['width']} {i['top'] + i['height']}; ppageno 0'>""")
                self.tab_count += 1
                self.started_page = True
            elif i['level'] == 2:
                self.block_count += 1
                self.add_to_str(
                    f"""<div class='ocr_carea' id='block_{self.page_count}_{self.block_count}' title="bbox {i['left']} {i['top']} {i['left'] + i['width']} {i['top'] + i['height']}">""")
                self.tab_count += 1
                self.started_block = True
            elif i['level'] == 3:
                self.par_count += 1
                self.add_to_str(
                    f"""<p class='ocr_par' id='par_{self.page_count}_{self.par_count}' title="bbox {i['left']} {i['top']} {i['left'] + i['width']} {i['top'] + i['height']}">""")
                self.tab_count += 1
                self.started_par = True
            elif i['level'] == 4:
                self.line_count += 1
                self.add_to_str(
                    f"""<span class='ocr_line' id='line_{self.page_count}_{self.line_count}' title="bbox {i['left']} {i['top']} {i['left'] + i['width']} {i['top'] + i['height']}">""")
                self.tab_count += 1
                self.started_line = True
            elif i['level'] == 5:
                self.word_count += 1
                self.add_to_str(
                    f"""<span class='ocrx_word' id='word_{self.page_count}_{self.word_count}' title='bbox {i['left']} {i['top']} {i['left'] + i['width']} {i['top'] + i['height']}; x_wconf {int(float(i['conf']))}'>{i['text']}</span>""")

        self.add_final_tags()
        return self._hocr_str
