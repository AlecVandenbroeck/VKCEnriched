import re


class PunctuationRemover:
    def process(self, extraction_output):
        cleaned_extraction_output = []
        times_replaced = 0
        previous_word = None
        for i in extraction_output:
            current_word = i['text']
            current_word, n = re.subn(r'(?<=[.])[,;\/:=?!)}^\]\-]|(?<=\?)[.,;\/:=)}^\]\-]|(?<=\!)[.,;\/:=)}^\]\-]|(?<=;)[.,;\/:=)}^\]\-!?]|(?<=\/)[.,;\/:=)}^\]\-!?]|(?<=:)[.,;\/:=)}^\]\-!?]|(?<=,)[.,;\/:=){^\]\-!?]', '', current_word)
            times_replaced += n
            if previous_word is not None:
                combined, n = re.subn(r'(?<=[.])[,;\/:=?!)}^\]\-]|(?<=\?)[.,;\/:=)}^\]\-]|(?<=\!)[.,;\/:=)}^\]\-]|(?<=;)[.,;\/:=)}^\]\-!?]|(?<=\/)[.,;\/:=)}^\]\-!?]|(?<=:)[.,;\/:=)}^\]\-!?]|(?<=,)[.,;\/:=){^\]\-!?]', '', previous_word + current_word)
                times_replaced += n
                current_word = combined[len(previous_word):]
            previous_word = current_word
            i['text'] = current_word
            cleaned_extraction_output.append(i)
        return cleaned_extraction_output, times_replaced
