from typing import List, Dict, Optional, TypedDict
from pydantic import BaseModel

class JobDetails(BaseModel):
    url: str = ""
    content: str = ""
    key_requirements: List[str] = []
    key_skills: List[str] = []
    key_competencies: List[str] = []

class ResumeDetails(BaseModel):
    content: str = ""
    key_experiences: List[str] = []
    key_achievements: List[str] = []
    key_skills: List[str] = []

class CompanyInfo(BaseModel):
    name: str = ""
    profile: str = ""
    culture: str = ""
    values: List[str] = []

class CoverLetterPlan(BaseModel):
    structure: List[str] = []
    key_points: List[str] = []
    matching_experiences: Dict[str, str] = {}

class CoverLetterContent(BaseModel):
    content: str = ""
    style: str = "professional"
    instructions: str = ""

class QAFeedback(BaseModel):
    score: int = 0
    feedback: str = ""
    suggestions: List[str] = []
    approved: bool = False

class GraphState(TypedDict):
    job_details: JobDetails
    resume_details: ResumeDetails
    company_info: CompanyInfo
    plan: CoverLetterPlan
    cover_letter: CoverLetterContent
    qa_feedback: QAFeedback
    iteration_count: int
    next_agent: str
    messages: List[str]
