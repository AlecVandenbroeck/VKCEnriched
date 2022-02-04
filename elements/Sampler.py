# Filter out pages from google + covers (now just leaves out the first and last 10 pages)

import os
import random
import numpy as np


class Sampler:
    def process(self, dir_path, n):
        files_list = np.asarray(sorted(os.listdir(dir_path)))
        number_of_pages = len(files_list) - 20
        sample_indices = random.sample(range(10, 10 + number_of_pages), n)
        return files_list[sample_indices]
