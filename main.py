from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from typing import List, Callable
import shutil
import beyondchaosmaster as BC


app = FastAPI()
templates = Jinja2Templates(directory="templates/")


## These both work
@app.post("/upload")
def create_file(upload_file: UploadFile = File(...)):
    upload_path = Path('roms/', upload_file.filename)
    try:
        with upload_path.open("wb+") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

@app.post("/files/upload")
def create_file(file: UploadFile = File(...)):
    file_object = file.file
    # Create empty file to copy the file_object to
    upload_folder = open(os.path.join('roms/', file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    return {"filename": file.filename}

@app.post("/gen_seed")
def generate_seed(file: UploadFile = File(...)):
    fileobj = file.file
    # consider using https://www.tutorialspoint.com/How-can-I-make-one-Python-file-run-another
    gen_seed = BC.randomizer.randomize(fileobj)
    return gen_seed


@app.get("/")
async def main():
    content = """
<body>
<p>Upload Files</p>
<form action="/files/upload" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)



# Taken from:
# https://github.com/eugeneyan/fastapi-html
# https://eugeneyan.com/writing/how-to-set-up-html-app-with-fastapi-jinja-forms-templates/


@app.get("/rest")
def read_item(num: int):
    result = spell_number(num)
    return {"number_spelled": result}


@app.get("/form")
def form_post(request: Request):
    result = "Type a number"
    # Find out what templateresponses are doing
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result})

@app.post('/checkbox')
def form_post(request: Request, num: int = Form(...), multiply_by_2: bool = Form(False)):
    result = spell_number(num, multiply_by_2)
    return templates.TemplateResponse('checkbox.html', context={'request': request, 'result': result, 'num': num})


@app.get("/download/")
def form_post(request: Request, num: int = Form(...), 
              multiply_by_2: bool = Form(False), action: str = Form(...)):
    if action == 'convert':
        result = spell_number(num, multiply_by_2)
        return templates.TemplateResponse('download.html', context={'request': request, 'result': result, 'num': num})
    elif action == 'download':
        # Requires aiofiles
        result = spell_number(num, multiply_by_2)
        filepath = save_to_text(result, num)
        return FileResponse(filepath, media_type='application/octet-stream', filename=f'{num}.txt')