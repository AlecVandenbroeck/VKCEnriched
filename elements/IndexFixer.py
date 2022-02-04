class IndexFixer:
    def process(self, extraction_output):
        cleaned_extraction_output = []
        word_index, line_index, par_index, block_index = 0, 0, 0, 0
        last_word_index, last_line_index, last_par_index, last_block_index = 0, 0, 0, 0
        for i in extraction_output:
            if len(cleaned_extraction_output) == 0:
                pass
            elif i['block_num'] != last_block_index:
                block_index += 1
                par_index, line_index, word_index = 0, 0, 0
            elif i['par_num'] != last_par_index:
                par_index += 1
                line_index, word_index = 0, 0
            elif i['line_num'] != last_line_index:
                line_index += 1
                word_index = 0
            else:
                word_index += 1

            last_word_index, last_line_index, last_par_index, last_block_index = i['word_num'], i['line_num'], i['par_num'], i['block_num']
            i['block_num'] = block_index
            i['par_num'] = par_index
            i['line_num'] = line_index
            i['word_num'] = word_index
            cleaned_extraction_output.append(i)
        return cleaned_extraction_output
