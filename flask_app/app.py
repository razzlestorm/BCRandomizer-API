# STD IMPORTS
import logging
import os
import sys

# 3RD PARTY IMPORTS
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, \
request, session, url_for, send_from_directory
from werkzeug.utils import secure_filename

# LOCAL IMPORTS

sys.path.append("./beyondchaosmaster")
from beyondchaosmaster.randomizer import randomize
from beyondchaosmaster.options import ALL_FLAGS, ALL_CODES

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
    rfile = request.files['file']
    if rfile and allowed_file(rfile.filename):
        filename = secure_filename(rfile.filename)
        rfile.save(os.path.join(upload_folder, filename))
        print(rfile)
        print(filename)
        return redirect(url_for("options", rom_name=filename))

## Route to choose options
@app.route("/options/<rom_name>", methods=["GET", "POST"])
def options(rom_name):
    if request.method == "POST":
        # We see the values the user has checked
        romfile = os.path.join(upload_folder, rom_name)
        flagcodes = {}
        flagcodes['rom_name'] = rom_name
        return redirect(url_for("randomize_file", flags_dict=flags))
    return render_template("options.html", options=flagcodes)

## Route to run program
@app.route("/randomize_file/<rom_name>", methods=["GET", "POST"])
def randomize_file(flags_dict):
    romfile = os.path.join(upload_folder, rom_name)
    args = [romfile]
    # Add options to args
    edited_file=randomize(args)
    print(type(edited_file))
    return render_template("options.html", romname=rom_name)

## Route to serve modded ROM file
@app.route("/serve_file/<rom_name>", methods=["GET", "POST"])
def serve_file(rom_name):
    return send_from_directory(upload_folder, filename=rom_name, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)