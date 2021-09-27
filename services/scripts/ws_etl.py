
from fastapi import FastAPI, File, UploadFile, HTTPException

from etl import ETL
from models import Errors


app = FastAPI()


@app.get('/')
def root():
    return {'hello': 'ws_etl'}


@app.post("/submit_document/")
async def create_file(file: UploadFile = File(...)):
    with open(f'/tmp/{file.filename}', 'wb') as f:
        f.write(file.file.read())

    try:
        etl = ETL(f'/tmp/{file.filename}')
        etl.main()
    except Exception as e:
        Errors.create(
            filename=file.filename,
            error=f"Failed process of etl: {e}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Failed process of etl: {e}"
        )

    return {
        "file_name": file.filename
    }