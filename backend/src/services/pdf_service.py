from pypdf import PdfReader
from fastapi import UploadFile
from backend.src.core.exceptions import PDFExtractionError
import io

class PDFService:
    @staticmethod
    async def extract_text(file: UploadFile, max_pages: int = 30) -> str:
        try:
            content = await file.read()
            reader = PdfReader(io.BytesIO(content))
            text = ""
            # Limit pages to prevent token overflow
            pages_to_read = min(len(reader.pages), max_pages)
            for i in range(pages_to_read):
                text += reader.pages[i].extract_text() or ""
            return text
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract text from PDF: {str(e)}")
