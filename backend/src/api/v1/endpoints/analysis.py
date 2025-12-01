from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.src.domain.models import AnalysisResponse
from backend.src.services.pdf_service import PDFService
from backend.src.services.llm_service import LLMService
from backend.src.core.exceptions import PDFExtractionError, LLMAnalysisError

router = APIRouter()

def get_llm_service():
    return LLMService()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_risk(
    file: UploadFile = File(...),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Upload a PDF 10-K report and get a risk analysis.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    try:
        # 1. Extract Text
        text = await PDFService.extract_text(file)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
        # 2. Analyze with LLM
        result = llm_service.analyze_risks(text)
        return result
        
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LLMAnalysisError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
