# STD IMPORTS
import logging
import os
import sys

# 3RD PARTY IMPORTS
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, \
request, session, url_for, send_from_directory, json
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
@app.route("/options/", methods=["GET", "POST"])
def options():
    rom_name = request.args.get('rom_name')
    romfile = os.path.join(upload_folder, rom_name)
    flags = {flag.name: (flag.attr, flag.description) for flag in ALL_FLAGS}
    codes = {code.name: (code.description, code.long_description, code.category) for code in ALL_CODES}
    if request.method == "POST":
        # We see the values the user has checked
        # for code in all_codes+all_flags:
        flagcodes = {**flags, **codes}
        print(request.form.get("flags"), request.form.get("codes"))
        # {k:v for k, v in request.form.items()} will return a dict of everything
        flagcodes = json.dumps({k:v for k, v in request.form.items()})
        print(flagcodes)
        return redirect(url_for("randomize_file", flags_dict=flagcodes, rom_name=rom_name))
    return render_template("options.html", flags=flags, codes=codes, rom_name=rom_name)

## Route to run program
@app.route("/randomize_file/", methods=["GET", "POST"])
def randomize_file():
    romfile = os.path.join(upload_folder, request.args.get('rom_name'))
    input_codes = json.loads(request.args.get('flags_dict'))
    args = [romfile, input_codes]
    # Add options to args
    #breakpoint()
    edited_file=randomize(args)
    print(type(edited_file))
    return render_template("options.html", rom_name=rom_name)

## Route to serve modded ROM file
@app.route("/serve_file/", methods=["GET", "POST"])
def serve_file():
    return send_from_directory(upload_folder, filename=rom_name, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)