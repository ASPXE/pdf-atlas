from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from v1.auth.router import get_current_user
from pdf2image import convert_from_bytes
import pytesseract
from datetime import datetime, timezone
from v1.scans.models import Scans
from v1.bd.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

scans_router = APIRouter(
    prefix="/scans",
    tags=["Scans"],
    responses={404: {"message": "Scans not found"}},
    dependencies=[Depends(get_current_user)]
)

@scans_router.get("/greetings")
async def greetings():
    return {"message": "Hello from scans endpoint"}

def extract_text_from_pdf(pdf_bytes):

    extracted_text = ""
    for page_number, image in enumerate(pdf_bytes):
        text = pytesseract.image_to_string(image, lang="eng")
        extracted_text += f"\n\n--- Page {page_number + 1} ---\n{text}"

    return {"text": extracted_text}


@scans_router.post("/upload-pdf")
async def upload_pdf(db: AsyncSession = Depends(get_db), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    file_bytes = await file.read()
    scan_started = datetime.now(timezone.utc)

    try:
        pdf_images = convert_from_bytes(file_bytes)
        response = extract_text_from_pdf(pdf_images)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while trying to convert the PDF: {str(e)}")

    scan_ended = datetime.now(timezone.utc)

    scanned_file = Scans(
        scan_started=scan_started,
        scan_ended=scan_ended,
        file_name=file.filename,
        file_bytes_size=len(file_bytes),
        user_id=current_user["id"]
    )

    db.add(scanned_file)
    db.commit()
    db.refresh(scanned_file)

    return {
        "message": "File processed successfully.",
        **response
    }

    
