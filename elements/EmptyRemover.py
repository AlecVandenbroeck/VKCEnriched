class EmptyRemover:
    def process(self, extraction_output):
        cleaned_extraction_output = []
        times_replaced = 0
        for i in extraction_output:
            if not i['text'] == '' and not i['text'] == ' ':
                cleaned_extraction_output.append(i)
            else:
                times_replaced += 1
        return cleaned_extraction_output, times_replaced
