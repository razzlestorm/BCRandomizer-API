# STD IMPORTS
import asyncio
import os
import pathlib
from random import choice
import sys
from uuid import uuid1

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, \
                  request, url_for, send_file, json
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# LOCAL IMPORTS
sys.path.append(sys.path[0] + "\\beyondchaosmaster")

# For Heroku
sys.path.append("/app/flask_app")
sys.path.append("/app/flask_app/beyondchaosmaster")
from beyondchaosmaster.randomizer import randomize
from beyondchaosmaster.options import ALL_FLAGS, ALL_CODES, ALL_MODES


# COMMENT OUT FOR HEROKU
# Uncomment for local
load_dotenv(verbose=True)


app = Flask(__name__)
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY
allowed_extensions = os.getenv('ALLOWED_EXTENSIONS')
upload_folder = os.getenv('UPLOAD_FOLDER')
debug_mode = os.getenv('DEBUG_MODE')
sockio = SocketIO(app)



# go through process of getting user input for flags and the like
# emit from html to a route that will start the randomization process, store that task id somewhere? Or store the key?
# emit from html to redirect to a waiting html page, which will continually ping the task
# emit from flask once task is finished
# When the waiting html recieves that emit from the finished task, redirect and serve up files



# task storage
task_storage = {}

def make_task_id():
    return str(uuid1())

def allowed_file(filename, checklist):
    """
    checks if a file extension is one of the allowed extensions
    """
    return '.' and filename.rsplit(".", 1)[1].lower() in checklist

'''
def run_randomizer(args):
    print("RANDOMIZATION BEGINNING")
    return randomize(args)
'''

@app.route("/", methods=["GET"])
def index():
    """Display basic webpage"""
    return render_template("index.html")

async def run_randomizer(args):
    loop = asyncio.get_event_loop()
    rom = await loop.run_in_executor(None, randomize, args)
    return rom

# Route to upload ROM
@app.route("/", methods=["POST"])
def upload():
    upload =  request.files
    if 'file' not in upload:
        flash("Please choose a file to upload")
        return redirect(url_for("index"))
    if upload and allowed_file(upload['file'].filename, allowed_extensions):
        filename = secure_filename(upload['file'].filename)
        upload['file'].save(os.path.join(upload_folder, filename))
        # Check to make sure things are correct
        print(upload)
        print(filename)
        return redirect(url_for("options", rom_name=filename))


# Route to choose options
@app.route("/options/", methods=["GET", "POST"])
def options():
    rom_name = request.args.get('rom_name')
    flags = {flag.name: (flag.attr, flag.description) for flag in ALL_FLAGS}
    codes = {code.name: (code.description,
                         code.long_description,
                         code.category) for code in ALL_CODES}
    modes = {mode.name: mode.description for mode in ALL_MODES}
    defaults = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'i',
                'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'w', 'y', 'z', 'johnnydmad',
                'makeover', 'partyparty']
    if request.method == "POST":
        # We see the values the user has checked
        # for code in all_codes+all_flags:
        # NOTE: This doesn't currently filter flags based on mod
        form =  request.form
        seed = form.get('seed')
        mode = form.get('mode')
        input_codes = [k for k in form.keys()]
        print(input_codes)
        romfile = os.path.join(upload_folder, rom_name)
        args = [romfile, seed, mode, input_codes[2:]]
        task_id = make_task_id()
        task_storage[task_id] = asyncio.run(run_randomizer(args))
        # If this doesn't work, emit to html to switch to a new page, then run this blockingly~~~~
        # then emit once task is done
        print("TASK CREATED")
        return redirect(url_for("waiting", task_id=task_id))
    return render_template("options.html",
                                 defaults=defaults,
                                 flags=flags,
                                 codes=codes,
                                 modes=modes,
                                 rom_name=rom_name)


def task_check(task_id):
    print("Task Checking STARTED...")
    try:
        task = task_storage[task_id]
    except KeyError:
        return f'Unknown task ID: {task_id}', 404
    except asyncio.CancelledError:
        return "The task was cancelled"

    if task.done():
        breakpoint()
        # check for exceptions
        # do something
        return task_id
    else:
        breakpoint()
        # return something?
        return False


@app.route("/waiting/<task_id>", methods=["GET"])
def waiting(task_id):
    print("WAITING ROUTE HIT")
    while not task_check(task_id):
        image = choice(os.listdir('quart_app/templates/img'))
        image = os.path.join('img', image)
        return render_template("pleasewait.html",
                               wait_image=image)
        #redirect to waiting again after x seconds?
    return redirect(url_for("serve_files", rom_name=task_id))



# Route to serve modded ROM file
@app.route("/serve_files/<path:rom_name>", methods=["GET", "POST"])
def serve_files(rom_name):
    #seed = rom_name.split(".")[1]
    print(task_storage[rom_name])
    log = rom_name.replace('smc', 'txt')
    return render_template("serve_files.html",
                                 filename=rom_name,
                                 seed=seed,
                                 log=log)


@app.route("/serve_smc/<path:rom_name>", methods=["GET", "POST"])
def serve_smc(rom_name):
    print(pathlib.Path.cwd())
    print(rom_name)
    # Added /upload_folder for Heroku
    path = pathlib.Path(upload_folder, rom_name)
    print(path)
    try:
        smc =  send_file(path, as_attachment=True)
    except FileNotFoundError:
        path = pathlib.Path(r'quart_app', rom_name)
        smc =  send_file(path, as_attachment=True)
    print(smc)
    return smc


@app.route("/serve_log/<path:log_name>", methods=["GET", "POST"])
def serve_log(log_name):
    print(log_name)
    path = pathlib.Path(upload_folder, log_name)
    print(path)
    try:
        log =  send_file(path, as_attachment=True)
    except FileNotFoundError:
        path = pathlib.Path(r'quart_app', log_name)
        log =  send_file(path, as_attachment=True)
    print(log)
    return log

if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)
