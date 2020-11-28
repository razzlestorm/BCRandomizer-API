# STD IMPORTS
import logging
import os

# 3RD PARTY IMPORTS
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, session, url_for
from werkzeug.utils import secure_filename

# LOCAL IMPORTS

app = Flask(__name__)
# app.configs
load_dotenv()
app.config.from_pyfile('app_config.cfg')

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY
allowed_extensions = app.config['ALLOWED_EXTENSIONS']
upload_folder = app.config['UPLOAD_FOLDER'] 
debug_mode = app.config['DEBUG_MODE']
logging_file_name = app.config['LOGGING_FILE_NAME']
logging_file_size = app.config['LOGGING_FILE_SIZE']
logging_file_count = app.config['LOGGING_FILE_COUNT']
logging_file_level = app.config['LOGGING_FILE_LEVEL']
if SECRET_KEY is None:
    app.logger.error('Env variable FLASK_SECRET_KEY is not defined. Please set it with a custom secret value in ./.env')
    sys.exit(1)


def allowed_file(filename):
    return '.' and filename.rsplit(".", 1)[1].lower() in allowed_extensions

# Routes that we're going to want:
## Route to display webpage (this can just be the base route)
@app.route("/", methods=["GET"])
def index():
    """Display basic webpage"""
    return render_template("index.html")


## Route to upload ROM
@app.route("/", methods=["POST"])
def upload():
    if 'file' not in request.files:
        flash("Please choose a file to upload")
        return redirect(url_for("index"))
    file = request.files['file']
    print(file)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, filename))
        return redirect(url_for("randomize"))

## Route to run program
@app.route("/randomize", methods=["GET"])
def randomize():
    pass

## Route to serve modded ROM file
@app.route("/placeholder", methods=["GET", "POST"])
def serve_file():
    pass



if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)