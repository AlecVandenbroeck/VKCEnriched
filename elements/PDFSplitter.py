from pdf2image import convert_from_path, convert_from_bytes

import os
from PIL import Image
import glob
import shutil
from util.Counter import Counter


class PDFConverter:
    def process(self, path: str) -> str:
        # extract filename without extension
        filename = '.'.join(path.split('/')[-1].split('.')[:-1])
        base_path = '/'.join(path.split('/')[:-1])

        # create directories (if exists => remove it first)
        if os.path.exists(os.path.join(base_path, filename)):
            shutil.rmtree(os.path.join(base_path, filename))
        os.mkdir(os.path.join(base_path, filename))

        _ = convert_from_path(path, output_folder=os.path.join(base_path, filename), output_file=Counter().count())

        # Fix naming from 10001-1.ppm to 00001.ppm
        for f in os.listdir(os.path.join(base_path, filename)):
            os.rename(os.path.join(base_path, filename, f), os.path.join(base_path, filename, f.split('-')[-1].zfill(9)))

        # Convert images from .ppm format to .png format
        for im_file in os.listdir(os.path.join(base_path, filename)):
            im = Image.open(os.path.join(base_path, filename, im_file))
            im_file_no_ext = im_file.split('.')[0]
            im.save(os.path.join(base_path, filename, f'{im_file_no_ext}.png'))

        # Remove .ppm images
        ppm_images = glob.glob(os.path.join(base_path, filename, '*.ppm'))
        for ppm_image in ppm_images:
            os.remove(ppm_image)

        return filename
