from openai import OpenAI
import json
from backend.src.core.config import settings
from backend.src.core.exceptions import LLMAnalysisError
from backend.src.domain.models import AnalysisResponse, RiskFactor

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY
        )

    def analyze_risks(self, text_chunk: str) -> AnalysisResponse:
        system_prompt = """
        You are a senior financial analyst. Your job is to extract 'Risk Factors' from 10-K reports.
        
        INSTRUCTIONS:
        1. Read the provided text.
        2. Identify the top 5 most critical specific risks (e.g. 'Supply Chain Disruption', 'Regulatory Change').
        3. Score their severity from 1-10.
        4. Categorize them into: 'Market', 'Operational', 'Regulatory', or 'Financial'.
        
        OUTPUT FORMAT:
        Return ONLY a valid JSON object with this structure:
        {
            "risks": [
                {
                    "risk_title": "Short Title",
                    "category": "Category Name",
                    "severity_score": 8,
                    "description": "One sentence summary of why this is a risk."
                }
            ]
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this 10-K excerpt: \n\n{text_chunk[:12000]}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            if "risks" not in data:
                raise ValueError("Invalid response format: 'risks' key missing")
                
            risks = [RiskFactor(**r) for r in data["risks"]]
            
            return AnalysisResponse(
                risks=risks,
                total_risks=len(risks),
                critical_risk_count=sum(1 for r in risks if r.severity_score >= 8)
            )
            
        except Exception as e:
            raise LLMAnalysisError(f"LLM Analysis failed: {str(e)}")
