from fastapi import FastAPI, File, UploadFile, HTTPException
from pipeline import ExtractionPipeline
from config import PIPELINE_CFG
import shutil
import os
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Extraction API")
pipeline = ExtractionPipeline(PIPELINE_CFG)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Document Extraction API...")
    # Optional: trigger lazy loading of models during startup
    if not PIPELINE_CFG.lazy_load:
        logger.info("Warming up models...")
        _ = pipeline.ocr_engine
        _ = pipeline.llm_engine
    logger.info("API ready.")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/extract")
async def extract_document(file: UploadFile = File(...), debug: bool = False):
    # Save the uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        logger.info(f"Received file: {file.filename}, format detected: {suffix}")
        result = pipeline.run(tmp_path, debug=debug)
        return {
            "filename": file.filename,
            "data": result.json,
            "is_valid": result.is_valid,
            "errors": result.validation_errors,
            "elapsed": result.elapsed_seconds,
            "format": result.source_format
        }
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
