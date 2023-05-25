# convert.py

import json
import os.path
from base64 import b64decode
from pathlib import Path


class DecodeResponse:
    def __init__(self, json_file, image_dir, data_dir='Data/Responses'):
        self.data_dir = data_dir
        self.json_file = json_file
        self.image_dir = image_dir
        if not os.path.exists(image_dir):
            p = Path(image_dir)
            p.mkdir(parents=True)

    def generate_image(self):
        with open(self.json_file, mode="r", encoding="utf-8") as file:
            response = json.load(file)

        for index, image_dict in enumerate(response["data"]):
            image_data = b64decode(image_dict["b64_json"])
            image_file = self.image_dir + f"/image-{index}.png"
            with open(image_file, mode="wb") as png:
                png.write(image_data)
        return image_file
