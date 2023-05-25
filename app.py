import os
import Model.dall_e as dall_e
import Model.decode_base64 as decode_base64
import Model.combine as combine
import Model.digitalocean as digitalocean
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response, send_file,render_template, abort
import datetime as dt
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
FolderPath = r"{}".format(Path("Data").parent.absolute())
print(FolderPath)

# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
# db = SQLAlchemy(app)

load_dotenv()

client = digitalocean.get_spaces_client(
    region_name=os.getenv('AWS_REGIONN_NAME'),
    endpoint_url=os.getenv('AWS_ENDPOINT'),
    key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

@app.route('/')
def index():
    return "Hello World!!!"

@app.route('/generate', methods=['POST'])
def generate_image():

    try:
        data_dir = os.getenv("DATA_DIR")
        image_dir = os.getenv("IMAGE_DIR")
        json_file = os.getenv("JSON_FILE")
        size = '1024x1024'
        # prompt1 = input("Apa karakter kesukaanmu? ")
        # prompt2 = input("Hobi atau kesukaanmu apa? ")
        data = request.get_json()
        prompt = f""" {data['character']} is my favorite character
        Please generate an image for my phone wallpaper of {data['character']} doing {data['activity']}
        The image should captured with a high-quality camera, using a shallow depth-of-field to create a blurred background and emphasize the subject"""
        # name = prompt1 + prompt2
        name = data['character'] + data['activity']
        model = dall_e.ModelAI(prompt, name, size)
        model.create()

        file_name = model.save_response()
        json_file = json_file + f'/{file_name}'
        image_dir = image_dir + f'/{file_name[:-5]}'

        image_result = decode_base64.DecodeResponse(json_file, image_dir)
        background_image = image_result.generate_image()

        result = combine.TheImages(file_name, background_image)
        result_path = result.create()
        print(f"RESULT PATH: {result_path}")
        try:
            result_upload = digitalocean.upload_file_to_space(client, os.getenv('AWS_BUCKET_NAME'), result_path, f"dalle/{result_path}")
            print(f"RESULT UPLOAD: {result_upload}")
        except :
            return make_response(jsonify({'message': 'error uploading image'}), 500)

        return make_response(jsonify({'message': 'image created'}), 201)
    except:
        return make_response(jsonify({'message': 'error creating image'}), 500)

def getReadableByteSize(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def getTimeStampString(tSec: float) -> str:
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj, '%Y-%m-%d %H:%M:%S')
    return tStr

def getIconClassForFilename(fName):
    fileExt = Path(fName).suffix
    fileExt = fileExt[1:] if fileExt.startswith(".") else fileExt
    fileTypes = ["aac", "ai", "bmp", "cs", "css", "csv", "doc", "docx", "exe", "gif", "heic", "html", "java", "jpg", "js", "json", "jsx", "key", "m4p", "md", "mdx", "mov", "mp3",
                 "mp4", "otf", "pdf", "php", "png", "pptx", "psd", "py", "raw", "rb", "sass", "scss", "sh", "sql", "svg", "tiff", "tsx", "ttf", "txt", "wav", "woff", "xlsx", "xml", "yml"]
    fileIconClass = f"bi bi-filetype-{fileExt}" if fileExt in fileTypes else "bi bi-file-earmark"
    return fileIconClass

# route handler
@app.route('/reports/', defaults={'reqPath': 'Data'})
@app.route('/reports/<path:reqPath>')
def getFiles(reqPath):
    # Join the base and the requested path
    # could have done os.path.join, but safe_join ensures that files are not fetched from parent folders of the base folder
    absPath = os.path.join(FolderPath, reqPath)

    # Return 404 if path doesn't exist
    if not os.path.exists(absPath):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(absPath):
        return send_file(absPath)

    # Show directory contents
    def fObjFromScan(x):
        fileStat = x.stat()
        # return file information for rendering
        return {'name': x.name,
                'fIcon': "bi bi-folder-fill" if os.path.isdir(x.path) else getIconClassForFilename(x.name),
                'relPath': os.path.relpath(x.path, FolderPath).replace("\\", "/"),
                'mTime': getTimeStampString(fileStat.st_mtime),
                'size': getReadableByteSize(fileStat.st_size)}
    fileObjs = [fObjFromScan(x) for x in os.scandir(absPath)]
    # get parent directory url
    parentFolderPath = os.path.relpath(
        Path(absPath).parents[0], FolderPath).replace("\\", "/")
    return render_template('files.html.j2', data={'files': fileObjs,
                                                 'parentFolder': parentFolderPath})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

#     prompt = f"""
#     {prompt1} is my favorite character
# Please generate an image for printed t-shirt of {prompt1} doing {prompt2}
# The image should captured with a high-quality camera and the image background should in a home built in a huge Soap bubble, with windows, doors, porches, awnings, the middle of space, cyberpunk lights.
#     """


