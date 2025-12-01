# FastAPI Backend Walkthrough

I have successfully implemented a production-ready FastAPI backend for the Financial Risk Analyzer, following Clean Architecture principles.

## Architecture Overview

The application is now split into two services:
1.  **Backend (`:8000`)**: FastAPI application handling business logic, PDF processing, and LLM integration.
2.  **Frontend (`:8501`)**: Streamlit application (currently standalone, but ready to be connected to the backend).

### Directory Structure
```
backend/
├── src/
│   ├── api/                # API Endpoints (Controllers)
│   │   ├── v1/endpoints/analysis.py
│   │   └── router.py
│   ├── core/               # Configuration & Exceptions
│   ├── domain/             # Pydantic Models (RiskFactor, AnalysisResponse)
│   ├── services/           # Business Logic
│   │   ├── pdf_service.py  # PDF Text Extraction
│   │   └── llm_service.py  # LLM Integration
│   └── main.py             # App Entrypoint
```

## API Documentation

The backend provides the following endpoints:

### `POST /api/v1/analysis/analyze`
Upload a PDF 10-K report to extract and analyze risk factors.

**Request:** `multipart/form-data`
- `file`: PDF file

**Response:** `application/json`
```json
{
  "risks": [
    {
      "risk_title": "Supply Chain Disruption",
      "category": "Operational",
      "severity_score": 8,
      "description": "..."
    }
  ],
  "total_risks": 1,
  "critical_risk_count": 1
}
```

### `GET /health`
Health check endpoint. Returns `{"status": "ok"}`.

## How to Run

The entire stack is containerized.

1.  **Start the services:**
    ```bash
    docker-compose up --build
    ```

2.  **Access the API Docs:**
    Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive Swagger UI.

3.  **Access the Frontend:**
    Open [http://localhost:8501](http://localhost:8501).

## Next Steps
- Update the Streamlit frontend (`app.py`) to consume the new FastAPI backend instead of running logic locally.
