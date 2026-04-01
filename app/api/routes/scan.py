import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from google.cloud import vision

router = APIRouter(tags=["scan"])

def find_value_near(label, lines, max_distance=3):
    for i, line in enumerate(lines):
        if label.lower() in line.lower():
            nums = re.findall(r"\d+[.,]?\d*", line)
            if nums:
                return nums[0].replace(",", ".")
            for j in range(1, max_distance + 1):
                if i + j < len(lines):
                    nums = re.findall(r"\d+[.,]?\d*", lines[i + j])
                    if nums:
                        return nums[0].replace(",", ".")
    return None

def find_value_with_unit(label, lines, unit="cm", max_distance=3):
    pattern = rf"(\d+[.,]?\d*)\s*{unit}"
    for i, line in enumerate(lines):
        if label.lower() in line.lower():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).replace(",", ".")
            for j in range(1, max_distance + 1):
                if i + j < len(lines):
                    match = re.search(pattern, lines[i + j], re.IGNORECASE)
                    if match:
                        return match.group(1).replace(",", ".")
    return None


@router.post("/scan-measurement")
async def scan_measurement(file: UploadFile = File(...)):
    content = await file.read()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise HTTPException(status_code=500, detail=response.error.message)

    text = response.full_text_annotation.text
    lines = text.split("\n")

    data = {
        "wzrost": find_value_with_unit("Wzrost", lines, unit="cm"),
        "masa_ciala": find_value_near("M. ciała", lines),
        "miesnie": find_value_near("Mięśnie", lines),
        "tluszcz": find_value_near("Tłuszcz", lines),
        "vfa": find_value_near("VFA", lines),
        "pbf": find_value_near("PBF", lines),
        "data": find_value_near("Data", lines),

        "segmental_beztluszczowa": {
            "lewa_reka": find_value_near("L. Ręka", lines),
            "prawa_reka": find_value_near("P. Ręka", lines),
            "tulow": find_value_near("Tułów", lines),
            "lewa_noga": find_value_near("L. Noga", lines),
            "prawa_noga": find_value_near("P. Noga", lines),
        },

        "segmental_tluszczowa": {
            "lewa_reka": find_value_near("L. Ręka", lines[lines.index(next(l for l in lines if "L. Ręka" in l)) + 1:], max_distance=3),
            "prawa_reka": find_value_near("P. Ręka", lines[lines.index(next(l for l in lines if "P. Ręka" in l)) + 1:], max_distance=3),
            "tulow": find_value_near("Tułów", lines[lines.index(next(l for l in lines if "Tułów" in l)) + 1:], max_distance=3),
            "lewa_noga": find_value_near("L. Noga", lines[lines.index(next(l for l in lines if "L. Noga" in l)) + 1:], max_distance=3),
            "prawa_noga": find_value_near("P. Noga", lines[lines.index(next(l for l in lines if "P. Noga" in l)) + 1:], max_distance=3),
        }
    }

    return data
