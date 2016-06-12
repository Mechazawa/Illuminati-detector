from flask import Flask, render_template, request, abort, redirect, send_from_directory
from detector import detect_illuminati
from uuid import uuid4
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

mime_whitelist = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'image/bitmap'
]


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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

    checksum = detect_illuminati(path)
    os.remove(path)
    return redirect('/result/{}'.format(checksum))


@app.route('/result/<checksum>', methods=['GET'])
def show_result(checksum):
    image_path = 'static/images/cache/{}_confirmed.jpg'.format(checksum)
    if not os.path.exists(image_path):
        image_path = None

    return render_template('display_result.html', image_path=image_path)

if __name__ == '__main__':
    app.run('127.0.0.1', 1337, True)
