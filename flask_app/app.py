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

#for local
sys.path.append(sys.path[0] + "/flask_app")
sys.path.append(sys.path[0] + "/flask_app/beyondchaosmaster")

#For Heroku
sys.path.append("/app/flask_app")
sys.path.append("/app/flask_app/beyondchaosmaster")
from beyondchaosmaster.randomizer import randomize
from beyondchaosmaster.options import ALL_FLAGS, ALL_CODES, ALL_MODES

app = Flask(__name__)
# app.configs
# CHANGE FOR HEROKU
'''
load_dotenv()
app.config.from_pyfile('app_config.cfg')
'''

SECRET_KEY = os.getenv('FLASK_SECRET_KEY') 
app.config['SECRET_KEY'] = SECRET_KEY
# Change these to config[KEY] for local
allowed_extensions = os.getenv('ALLOWED_EXTENSIONS')
upload_folder = os.getenv('UPLOAD_FOLDER')
debug_mode = os.getenv('DEBUG_MODE')
print(allowed_extensions, upload_folder, debug_mode)
#logging_file_name = app.config['LOGGING_FILE_NAME']
#logging_file_size = app.config['LOGGING_FILE_SIZE']
#logging_file_count = app.config['LOGGING_FILE_COUNT']
#logging_file_level = app.config['LOGGING_FILE_LEVEL']
#if SECRET_KEY is None:
#    app.logger.error('Env variable FLASK_SECRET_KEY is not defined. Please set it with a custom secret value in ./.env')
#    sys.exit(1)


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
        print('CWD ', os.getcwd())
        print('SUBDIRECTORIES ', os.listdir())
        print('UPLOADS_FOLDER: ', os.listdir('flask_app/uploaded_files/'))
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
    modes = {mode.name: mode.description for mode in ALL_MODES}
    defaults = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'i',
                'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'w', 'y', 'z', 'johnnydmad',
                'makeover', 'partyparty']
    if request.method == "POST":
        # We see the values the user has checked
        # for code in all_codes+all_flags:
        flagcodes = {**flags, **codes}
        seed = request.form.get('seed')
        mode = request.form.get('mode')
        flagcodemode = json.dumps([k for k in request.form.keys()])
        return redirect(url_for("randomize_file", mode=mode, seed=seed, flags_list=flagcodemode, rom_name=rom_name))
    return render_template("options.html", defaults=defaults, flags=flags, codes=codes, modes=modes, rom_name=rom_name)

## Route to run program
@app.route("/randomize_file/", methods=["GET", "POST"])
def randomize_file():
    romfile = os.path.join(upload_folder, request.args.get('rom_name'))
    seed = request.args.get('seed')
    mode = request.args.get('mode')
    input_codes = json.loads(request.args.get('flags_list'))
    print(input_codes)
    args = [romfile, seed, mode, input_codes[2:]]
    # Add options to args
    outfile = randomize(args)
    # The edited_file name has the upload_folder attached to its path
    file_name = outfile.split("/")[-1]
    return redirect(url_for("serve_files", rom_name=file_name))

# Create independent route with buttons to serve ROM/TXT
## Route to serve modded ROM file
@app.route("/serve_files/<path:rom_name>", methods=["GET", "POST"])
def serve_files(rom_name):
    seed = rom_name.split(".")[1]
    log = rom_name.replace('smc', 'txt')
    return render_template("serve_files.html", filename=rom_name, seed=seed, log=log)

@app.route("/serve_smc/<path:rom_name>", methods=["GET", "POST"])
def serve_smc(rom_name):
    return send_from_directory('uploaded_files', filename=rom_name, as_attachment=True)

@app.route("/serve_log/<path:log_name>", methods=["GET", "POST"])
def serve_log(log_name):
    return send_from_directory('uploaded_files', filename=log_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)
