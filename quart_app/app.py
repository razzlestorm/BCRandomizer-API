# STD IMPORTS
import asyncio
import concurrent.futures
import os
import pathlib
from random import choice
import sys
from uuid import uuid1

from dotenv import load_dotenv
from quart import Quart, render_template, redirect, \
                  request, url_for, send_file, json
from quart.utils import run_sync
from werkzeug.utils import secure_filename

# LOCAL IMPORTS
sys.path.append(sys.path[0] + "\\beyondchaosmaster")

# For Heroku
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


# task storage
task_storage = {}

def make_task_id():
    return str(uuid1())

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
        await flash("Please choose a file to upload")
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
    flags = {flag.name: (flag.attr, flag.description) for flag in ALL_FLAGS}
    codes = {code.name: (code.description,
                         code.long_description,
                         code.category) for code in ALL_CODES}
    modes = {mode.name: mode.description for mode in ALL_MODES}
    defaults = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'i',
                'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'w', 'y', 'z', 'johnnydmad',
                'makeover', 'partyparty']

    def run_randomizer(args):
        print("RANDOMIZATION BEGINNING")
        return randomize(args)
    
    if request.method == "POST":
        # We see the values the user has checked
        # for code in all_codes+all_flags:
        # NOTE: This doesn't currently filter flags based on mod
        form = await request.form
        seed = form.get('seed')
        mode = form.get('mode')
        input_codes = [k for k in form.keys()]
        print(input_codes)
        romfile = os.path.join(upload_folder, rom_name)
        args = [romfile, seed, mode, input_codes[2:]]
        task_id = make_task_id()
        task_storage[task_id] = await run_sync(run_randomizer(args))
        print("TASK CREATED")
        return redirect(url_for("waiting", task_id=task_id))
    return await render_template("options.html",
                                 defaults=defaults,
                                 flags=flags,
                                 codes=codes,
                                 modes=modes,
                                 rom_name=rom_name)

# https://stackoverflow.com/questions/41063331/how-to-use-asyncio-with-existing-blocking-library
################ THIS SHOULD BE THE SOLUTION https://pgjones.gitlab.io/quart/how_to_guides/sync_code.html

'''
# Route to run program
@app.route("/randomize_file/", methods=["GET", "POST"])
async def randomize_file():
    romfile = os.path.join(upload_folder, request.args.get('rom_name')) 
    seed = request.args.get('seed')
    mode = request.args.get('mode')
    input_codes = json.loads(request.args.get('flags_list'))
    print(input_codes)
    args = [romfile, seed, mode, input_codes[2:]]
    
    # task.add_done_callback(redirect(url_for("serve_files", rom_name=file_name))
    # The edited_file name has the upload_folder attached to its path
    # print(task)
    # TODO: show waiting route while task is running
    # https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html
    
    return redirect(url_for("waiting", romfile=romfile, args=args))
'''




'''
from uuid import uuid1

import quart


def make_task_id():
    return str(uuid1())


background_tasks = {}

app = quart.Quart('my-api')


@app.route("/create-file", methods=["POST"])
async def form_handler():
    form_data = ... # get form data here and parse it out

    task_id = make_task_id()
    task = asyncio.create_task(create_file(form_data), name=task_id)
    background_tasks[task_id] = task

    # Return the task id with HTTP status 202 ("Accepted")
    # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202
    return task_id, 202
https://stackoverflow.com/questions/45226289/how-to-poll-python-asyncio-task-status

@app.route("/create-file-wait/<task_id>", methods=["GET"])
async def waiting(task_id):
    try:
        task = background_tasks[task_id]
    except KeyError:
        return f'Unknown task ID: {task_id}', 404

    await task

    if (exc := task.exception()) is not None:
        body, status = str(exc), 500
    else:
        created_file_data = task.result
        body, status = created_file_data, 200

    del background_tasks[task_id]
    return body, status

you might also want a way to GET a list of all currently running background jobs
fix error — Today at 8:14 PM
and remove tasks if nobody grabs them in a while, I suppose
salt rock lamp — Today at 8:14 PM
@app.route("/create-file-list", methods=["GET"])
async def waiting(task_id):
    return list(background_tasks.values())
yeah good idea, @fix error you might want to keep track of when the task was started and have some background job on a scheduler that deletes old tasks
RazzleStorm — Today at 8:18 PM
Hm, okay, I think I understand. Is the (exc := task.exception()) is not None block where I would be checking the task status? Ideally I'd like to be able to display one thing before the task is complete, but then display the task's data after it has completed.
Also thank you @salt rock lamp ! Storing the tasks in a dict makes sense.
salt rock lamp — Today at 8:30 PM
the exc :=  thing is because if the task raised an exception, that exception will be raised in your face when you try to retrieve the result
this is probably not the same as the success/failure status of the file creation operation itself, although they might be related
i also don't know how this is meant to work w/ your particular frontend
maybe instead of waiting for the task to complete, the client should have to poll for it


@app.route("/create-file-check/<task_id>", methods=["GET"])
async def create_file_check(task_id):
    try:
        task = background_tasks[task_id]
    except KeyError:
        return f'Unknown task ID: {task_id}', 404

    if task.done():
        # Do something with the completed task.
        # Don't forget to check for an exception!
        ...
    else:
        # Inform the client that the task is still in progress
        ...


for a real-world example of an API like this, see the Mailchimp "batch" API
https://mailchimp.com/developer/marketing/guides/run-async-requests-batch-endpoint/
https://mailchimp.com/developer/marketing/api/batch-operations/
'''



@app.route("/task-check/<task_id>", methods=["GET"])
async def task_check(task_id):
    print("Task Checking STARTED...")
    try:
        task = task_storage[task_id]
    except KeyError:
        return f'Unknown task ID: {task_id}', 404
    except asyncio.CancelledError:
        return "The task was cancelled"
    
    if task.done():
        # check for exceptions
        # do something
        return task_id
    else:
        # return something?
        return False
         


@app.route("/waiting/<task_id>", methods=["GET"])
async def waiting(task_id):


    print("WAITING ROUTE HIT")
    while not await task_check(task_id):
        image = choice(os.listdir('quart_app/templates/img'))
        image = os.path.join('img', image)
        await render_template("pleasewait.html",
                               wait_image=image)
        #redirect to waiting again after x seconds?
    return redirect(url_for("serve_files", rom_name=task_id))



# Route to serve modded ROM file
@app.route("/serve_files/<path:rom_name>", methods=["GET", "POST"])
async def serve_files(rom_name):
    #seed = rom_name.split(".")[1]
    print(task_storage[rom_name])
    log = rom_name.replace('smc', 'txt')
    return await render_template("serve_files.html",
                                 filename=rom_name,
                                 seed=seed,
                                 log=log)


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
        path = pathlib.Path(r'quart_app', rom_name)
        smc = await send_file(path, as_attachment=True)
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
        path = pathlib.Path(r'quart_app', log_name)
        log = await send_file(path, as_attachment=True)
    print(log)
    return log

if __name__ == '__main__':
    app.run(debug=debug_mode, port=5001)
