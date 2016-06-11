from flask import Flask, render_template, request, abort
from detector import detect_illuminati
import shutil
from uuid import uuid4

app = Flask(__name__)

mime_whitelist = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'image/bitmap'
]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/find', methods=['POST'])
def find_illuminati():
    if 'image' not in request.files:
        abort(400)

    file = request.files['image']
    if file.filename == '' or not file:
        abort(400)

    if file.mimetype.lower() not in mime_whitelist:
        abort(415)

    path = 'uploads/{}.{}'.format(uuid4().hex, file.filename.split('.')[-1])
    file.save(path)

    return render_template('find.html', image_path=detect_illuminati(path))

if __name__ == '__main__':
    app.run('127.0.0.1', 1337, True)
