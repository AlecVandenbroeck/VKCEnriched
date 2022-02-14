import csv
import os
import wget
import json

class IIIFScraper:
    def __init__(self, manifest_url: str):
        self.manifest_url = manifest_url
        self.manifest_path = None

    def download_manifest(self):
        self.manifest_path = wget.download(self.manifest_url)
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
            wget.download(url=i['images'][0]['resource']['@id'], out=os.path.join(base_path, f"{i['label']}.jpg"))

