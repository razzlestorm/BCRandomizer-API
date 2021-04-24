# STD IMPORTS
import logging
import os
import pathlib
from random import choice
import sys
 
from dotenv import load_dotenv
from quart import Quart, render_template, redirect, \
request, session, url_for, send_file, json
from werkzeug.utils import secure_filename

# LOCAL IMPORTS
sys.path.append(sys.path[0] + "\\beyondchaosmaster")

#For Heroku
sys.path.append("/app/quart_app")
sys.path.append("/app/quart_app/beyondchaosmaster") 
from beyondchaosmaster.randomizer import randomize
from beyondchaosmaster.options import ALL_FLAGS, ALL_CODES, ALL_MODES


# COMMENT OUT FOR HEROKU
# Uncomment for local
load_dotenv(verbose=True)


app = Quart(__name__)

SECRET_KEY = os.getenv('QUART_SECRET_KEY') 
app.config['SECRET_KEY'] = SECRET_KEY
allowed_extensions = os.getenv('ALLOWED_EXTENSIONS')
upload_folder = os.getenv('UPLOAD_FOLDER')
debug_mode = os.getenv('DEBUG_MODE')


def allowed_file(filename, checklist):
    """
    checks if a file extension is one of the allowed extensions
    """
    return '.' and filename.rsplit(".", 1)[1].lower() in checklist


@app.route("/", methods=["GET"])
async def index():
    """Display basic webpage"""
    return await render_template("index.html")


# Route to upload ROM
@app.route("/", methods=["POST"])
async def upload():
    upload = await request.files
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
async def options():
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
        # NOTE: This doesn't currently filter flags based on mode
        flagcodes = {**flags, **codes}
        form = await request.form
        seed = form.get('seed')
        mode = form.get('mode')
        flagcodemode = json.dumps([k for k in form.keys()])
        return redirect(url_for("randomize_file", mode=mode, seed=seed, flags_list=flagcodemode, rom_name=rom_name))
    return await render_template("options.html", defaults=defaults, flags=flags, codes=codes, modes=modes, rom_name=rom_name)

async def run_randomizer(args):
    print("RANDOMIZATION BEGINNING")
    return randomize(args)


# Route to run program
@app.route("/randomize_file/", methods=["GET", "POST"])
async def randomize_file():
    romfile = os.path.join(upload_folder, request.args.get('rom_name'))
    seed = request.args.get('seed')
    mode = request.args.get('mode')
    input_codes = json.loads(request.args.get('flags_list'))
    print(input_codes)
    args = [romfile, seed, mode, input_codes[2:]]
    task = await run_randomizer(args)
    # The edited_file name has the upload_folder attached to its path
    print(task)
    # TODO: show waiting route while task is running
    # https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
    file_name = task.split("/")[-1]
    return redirect(url_for("serve_files", rom_name=file_name))

'''
@app.route("/waiting/<task_id>", methods=["GET"]) 
async def waiting(task_id):
    task = run_randomizer.AsyncResult(task_id)
    # if not done, sleep for a second
    rom_name = request.args.get('rom_name')
    if task.status != "SUCCESS":
        # keep going
        return redirect(url_for("serve_files", rom_name=rom_name)) 

    image = choice(os.listdir('quart_app/templates/img'))
    image = os.path.join('img', image)
    breakpoint()
    return await render_temple("pleasewait.html", wait_image=image, task_id=task_id)
'''

# Route to serve modded ROM file
@app.route("/serve_files/<path:rom_name>", methods=["GET", "POST"])
async def serve_files(rom_name):
    seed = rom_name.split(".")[1]
    log = rom_name.replace('smc', 'txt')
    return await render_template("serve_files.html", filename=rom_name, seed=seed, log=log)

@app.route("/serve_smc/<path:rom_name>", methods=["GET", "POST"])
async def serve_smc(rom_name):
    print(pathlib.Path.cwd())
    print(rom_name)
    # Added /upload_folder for Heroku
    path = pathlib.Path(upload_folder, rom_name)
    print(path)
    try:
        smc = await send_file(path, as_attachment=True)
    except FileNotFoundError:
        smc = await send_file(pathlib.Path(r'quart_app', rom_name), as_attachment=True)
    print(smc)
    return smc

@app.route("/serve_log/<path:log_name>", methods=["GET", "POST"])
async def serve_log(log_name):
    print(log_name)
    path = pathlib.Path(upload_folder, log_name)
    print(path)
    try:
        log = await send_file(path, as_attachment=True)
    except FileNotFoundError:
        log = await send_file(pathlib.Path(r'quart_app', log_name), as_attachment=True)
    print(log)
    return log

if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)
