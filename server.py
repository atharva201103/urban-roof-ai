from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import time

# Import agents and tools from existing codebase
from agents.extraction_agent import run_extraction_agent
from agents.merge_agent import run_merge_agent
from agents.reasoning_agent import run_reasoning_agent
from agents.report_agent import run_report_agent
from agents.validation_agent import run_validation_agent
from tools.pdf_parser import extract_text_from_pdf
from tools.docx_parser import extract_text_from_docx
from tools.image_extractor import extract_images

app = FastAPI(title="Urban Roof Analysis API")

# Configure CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def call_with_retry(func, *args, max_retries=5):
    """Call a function with automatic retry and waiting on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 60 * (attempt + 1)
                print(f"⏳ Rate limited. Waiting {wait_time} seconds before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    print("❌ Max retries reached. Please try again later.")
    return None

@app.post("/api/analyze")
async def analyze_report(
    inspection_file: UploadFile = File(...),
    thermal_file: UploadFile = File(...)
):
    
    def validate_file(f):
        is_pdf = f.filename.lower().endswith('.pdf')
        is_docx = f.filename.lower().endswith('.docx')
        return is_pdf or is_docx

    if not validate_file(inspection_file) or not validate_file(thermal_file):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    # Ensure directories exist
    os.makedirs("input_docs", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    inspection_path = f"input_docs/{inspection_file.filename}"
    thermal_path = f"input_docs/{thermal_file.filename}"
    
    try:
        # Save both files
        with open(inspection_path, "wb") as buffer:
            shutil.copyfileobj(inspection_file.file, buffer)
        with open(thermal_path, "wb") as buffer:
            shutil.copyfileobj(thermal_file.file, buffer)
            
        print("Step 1: Extracting text from documents...")
        if inspection_file.filename.lower().endswith('.pdf'):
            inspection_text = extract_text_from_pdf(inspection_path)
            images1 = extract_images(inspection_path)
        else:
            inspection_text = extract_text_from_docx(inspection_path)
            images1 = []
            
        if thermal_file.filename.lower().endswith('.pdf'):
            thermal_text = extract_text_from_pdf(thermal_path)
            images2 = extract_images(thermal_path)
        else:
            thermal_text = extract_text_from_docx(thermal_path)
            images2 = []
            
        print("Step 2: Combining content...")
        combined_text = inspection_text + thermal_text
        images = images1 + images2
            
        print("Step 3: Running extraction agent...")
        observations = call_with_retry(run_extraction_agent, combined_text)
        
        print("Waiting 10 seconds before next API call...")
        time.sleep(10)
        
        print("Step 4: Running merge agent...")
        merged = call_with_retry(run_merge_agent, observations)
        
        print("Waiting 10 seconds before next API call...")
        time.sleep(10)
        
        print("Step 5: Running reasoning agent...")
        analysis = call_with_retry(run_reasoning_agent, merged)
        
        print("Waiting 10 seconds before next API call...")
        time.sleep(10)
        
        print("Step 6: Generating report...")
        report = call_with_retry(run_report_agent, analysis, images)
        
        print("Waiting 10 seconds before next API call...")
        time.sleep(10)
        
        print("Step 7: Validating report...")
        final_report = call_with_retry(run_validation_agent, report)
        
        # Save output for posterity
        output_path = "output/final_report.md"
        with open(output_path, "w") as f:
            f.write(final_report)
            
        return JSONResponse(content={
            "status": "success",
            "message": "Analysis completed successfully",
            "report": final_report
        })
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporarily uploaded files
        if os.path.exists(inspection_path):
            os.remove(inspection_path)
        if os.path.exists(thermal_path):
            os.remove(thermal_path)

# Serve the frontend files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("Starting server... Access the UI at http://localhost:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
