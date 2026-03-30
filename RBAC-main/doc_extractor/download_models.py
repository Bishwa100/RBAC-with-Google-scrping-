import os
import logging
from config import PIPELINE_CFG
from models import download_huggingface_model
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Downloading models for doc_extractor...")
    
    # Ensure weight directory exists
    os.makedirs(PIPELINE_CFG.weights_dir, exist_ok=True)

    # 1. Download TrOCR
    logger.info(f"Downloading TrOCR: {PIPELINE_CFG.ocr.trocr_model_id}")
    download_huggingface_model(PIPELINE_CFG.ocr.trocr_model_id, PIPELINE_CFG.weights_dir)

    # 2. Download Qwen (LLM)
    logger.info(f"Downloading LLM: {PIPELINE_CFG.llm.model_id}")
    download_huggingface_model(PIPELINE_CFG.llm.model_id, PIPELINE_CFG.weights_dir)

    # 3. EasyOCR (it downloads internally on first run, 
    # but we can trigger it by initializing)
    logger.info("Downloading EasyOCR models...")
    import easyocr
    easyocr_dir = os.path.join(PIPELINE_CFG.weights_dir, "easyocr")
    os.makedirs(easyocr_dir, exist_ok=True)
    _ = easyocr.Reader(
        PIPELINE_CFG.ocr.easyocr_languages,
        gpu=torch.cuda.is_available(),
        model_storage_directory=easyocr_dir,
        download_enabled=True
    )

    logger.info("All models downloaded successfully.")

if __name__ == "__main__":
    main()
