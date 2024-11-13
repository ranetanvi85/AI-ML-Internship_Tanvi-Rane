Python 3.11.4 (tags/v3.11.4:d2340ef, Jun  7 2023, 05:45:37) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import os
... import uuid
... from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
... from pydantic import BaseModel
... from typing import List
... from starlette.responses import JSONResponse
... from transcribe import transcribe_audio
... from summarize import summarize_text, create_medical_document
... 
... app = FastAPI()
... 
... transcription_tasks = []
... 
... class TranscriptionResult(BaseModel):
...     task_id: str
...     transcription: str = None
...     summary: str = None
...     status: str = "processing"
...     message: str = None
...     document_path: str = None
... 
... def background_task(file_location: str, task_id: str):
...     new_task = TranscriptionResult(task_id=task_id)
...     transcription_tasks.append(new_task)
... 
...     transcription, error = transcribe_audio(file_location)
...     if error:
...         new_task.status = "error"
...         new_task.message = error
...         return
... 
...     new_task.transcription = transcription
... 
...     summary, error = summarize_text(transcription)
...     if error:
        new_task.status = "error"
        new_task.message = error
        return

    new_task.summary = summary

    document_path = f"./documents/{task_id}_medical_report.docx"
    create_medical_document(transcription, summary, document_path)
    new_task.document_path = document_path
    new_task.status = "success"

    os.remove(file_location)

@app.post("/transcribe/start")
async def transcribe_audiofile(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_location = f"./audio/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    task_id = str(uuid.uuid4())
    background_tasks.add_task(background_task, file_location, task_id)

    return JSONResponse(content={"task_id": task_id}, status_code=201)

@app.get("/transcribe/status/{task_id}", response_model=TranscriptionResult)
async def get_transcription_result(task_id: str):
    task = next((task for task in transcription_tasks if task.task_id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task.dict(), status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
