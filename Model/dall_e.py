# create.py
import json
import os

import openai
from dotenv import load_dotenv
import logging
from pathlib import Path

load_dotenv()
logger = logging.getLogger(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


class ModelAI:
    def __init__(self, prompt, name,  size='256x256',  data_dir='Data/Responses'):
        self.prompt = prompt
        self.name = name
        self.size = size
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            p = Path(data_dir)
            p.mkdir()
        self.response = None

    def create(self):
        self.response = openai.Image.create(
            prompt=self.prompt,
            n=1,
            size=self.size,
            response_format="b64_json",
        )
        print("Image just created")

    def save_response(self):
        file_name = f"{self.name}-{self.response['created']}.json"
        file_path = self.data_dir + f'/{file_name}'

        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(self.response, file)
        return file_name
