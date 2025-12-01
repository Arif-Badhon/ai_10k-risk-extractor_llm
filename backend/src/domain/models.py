from pydantic import BaseModel, Field
from typing import List, Optional

class RiskFactor(BaseModel):
    risk_title: str = Field(..., description="Short title of the risk")
    category: str = Field(..., description="Category: Market, Operational, Regulatory, or Financial")
    severity_score: int = Field(..., ge=1, le=10, description="Severity score from 1 to 10")
    description: str = Field(..., description="One sentence summary of why this is a risk")

class AnalysisResponse(BaseModel):
    risks: List[RiskFactor]
    total_risks: int
    critical_risk_count: int
