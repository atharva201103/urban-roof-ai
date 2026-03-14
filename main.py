import time
from agents.extraction_agent import run_extraction_agent
from agents.merge_agent import run_merge_agent
from agents.reasoning_agent import run_reasoning_agent
from agents.report_agent import run_report_agent
from agents.validation_agent import run_validation_agent

from tools.pdf_parser import extract_text_from_pdf
from tools.image_extractor import extract_images


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


print("Step 1: Extracting text from PDFs...")
inspection_text = extract_text_from_pdf("input_docs/inspection_report.pdf")
thermal_text = extract_text_from_pdf("input_docs/thermal_report.pdf")
print("✅ Text extracted")

print("Step 2: Extracting images...")
images1 = extract_images("input_docs/inspection_report.pdf")
images2 = extract_images("input_docs/thermal_report.pdf")
images = images1 + images2
print(f"✅ {len(images)} images extracted")

combined_text = inspection_text + thermal_text

print("Step 3: Running extraction agent...")
observations = call_with_retry(run_extraction_agent, combined_text)
print("✅ Extraction done")

print("Waiting 10 seconds before next API call...")
time.sleep(10)

print("Step 4: Running merge agent...")
merged = call_with_retry(run_merge_agent, observations)
print("✅ Merge done")

print("Waiting 10 seconds before next API call...")
time.sleep(10)

print("Step 5: Running reasoning agent...")
analysis = call_with_retry(run_reasoning_agent, merged)
print("✅ Reasoning done")

print("Waiting 10 seconds before next API call...")
time.sleep(10)

print("Step 6: Generating report...")
report = call_with_retry(run_report_agent, analysis, images)
print("✅ Report generated")

print("Waiting 10 seconds before next API call...")
time.sleep(10)

print("Step 7: Validating report...")
final_report = call_with_retry(run_validation_agent, report)
print("✅ Validation done")

print("\n📋 FINAL REPORT:\n")
print(final_report)

print("\n💾 Saving report to output folder...")
import os
os.makedirs("output", exist_ok=True)
with open("output/final_report.md", "w") as f:
    f.write(final_report)
print("✅ Report successfully saved to output/final_report.md!")