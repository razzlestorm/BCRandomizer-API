from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from typing import List
import shutil

# https://github.com/eugeneyan/fastapi-html
# https://eugeneyan.com/writing/how-to-set-up-html-app-with-fastapi-jinja-forms-templates/


app = FastAPI()

@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    for f in files:
        with open(f.filename, "wb") as f2save:
            shutil.copyfileobj(f.file, f2save)
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    for f in files:
        with open(f.filename, "wb") as f2save:
            shutil.copyfileobj(f.file, f2save)
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<p>Create files</p>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<p>Upload files</p>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)