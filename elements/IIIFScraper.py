# TODO: make sure file numbering is set to fixed length
import os
import urllib.request
import json


class IIIFScraper:
    def __init__(self, manifest_url: str, manifest_path=None):
        self.manifest_url = manifest_url
        self.manifest_path = manifest_path

    def download_manifest(self):
        try:
            if self.manifest_path is not None:
                urllib.request.urlretrieve(self.manifest_url, filename=self.manifest_path)
            else:
                self.manifest_path = urllib.request.urlretrieve(self.manifest_url)
        finally:
            if self.manifest_path is None:
                print(f"""Couldn't download manifest at URL {self.manifest_url}""")

    def download_images(self):
        file_ext, _ = os.path.split(self.manifest_path)
        base_path = self.manifest_path.split('.')[0]
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        with open(self.manifest_path, 'r') as manifest_file:
            manifest = json.load(manifest_file)
        for i in manifest['sequences'][0]['canvases']:
            urllib.request.urlretrieve(i['images'][0]['resource']['@id'], os.path.join(base_path, f"{i['label']}.jpg"))
