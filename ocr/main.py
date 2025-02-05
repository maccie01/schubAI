from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import uvicorn

app = FastAPI()

# Initialize PaddleOCR with MKLDNN disabled
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',
    enable_mkldnn=False,
    show_log=False
)

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    contents = await file.read()
    # Process image and return results
    result = ocr.ocr(contents)
    return {"result": result}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 