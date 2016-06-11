from flask import Flask, render_template
from detector import detect_illuminati

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/find', methods=['POST'])
def find_illuminati():
    pass

if __name__ == '__main__':
    app.run('127.0.0.1', 1337)
