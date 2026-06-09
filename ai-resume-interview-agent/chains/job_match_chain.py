from typing import List

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class JobSkillGap(BaseModel):
    skill: str = Field(..., description="Skill, tool, keyword, or competency missing from the resume")
    importance: str = Field(..., description="Why this skill matters for the job description")
    evidence_from_job: str = Field(..., description="Short reference to the job description requirement")
    suggested_resume_location: str = Field(..., description="Where this could naturally be added if truthful")


class JobMatchResponse(BaseModel):
    match_score: int = Field(..., description="Resume-to-job match score from 0 to 100")
    matched_skills: List[str] = Field(default_factory=list, description="Skills found in both the resume and job description")
    missing_required_skills: List[JobSkillGap] = Field(default_factory=list, description="Must-have skills from the job description missing from the resume")
    missing_preferred_skills: List[JobSkillGap] = Field(default_factory=list, description="Nice-to-have skills from the job description missing from the resume")
    keyword_gaps: List[str] = Field(default_factory=list, description="Exact ATS keywords or phrases from the job description absent from the resume")
    recommendations: List[str] = Field(default_factory=list, description="Actionable resume changes grounded in truthful resume content")
    summary: str = Field(..., description="Brief overall assessment of fit and the biggest gaps")


def create_context(resume_text: str, job_description: str) -> str:
    return f"""
You are an expert ATS analyst and technical recruiter.

Compare the resume against the job description and identify missing skills or keywords.

Rules:
- Do not invent experience, projects, degrees, certifications, or skills.
- Mark a skill as missing only if it appears in the job description and is not supported by resume evidence.
- Separate required gaps from preferred/nice-to-have gaps when the job description makes that distinction.
- Recommend adding a skill only if the candidate can truthfully support it; otherwise recommend learning it or adding a related project.
- Keep recommendations concrete and concise.

Resume:
{resume_text}

Job Description:
{job_description}
"""


def analyze_job_match_chain(resume_text: str, job_description: str, llm):
    context = create_context(resume_text, job_description)
    prompt = ChatPromptTemplate.from_messages([("human", context)])

    try:
        structured_llm = llm.with_structured_output(JobMatchResponse)
    except NotImplementedError:
        structured_llm = None
    except Exception:
        structured_llm = None

    if structured_llm is not None:
        return prompt | structured_llm

    from langchain_core.messages import HumanMessage

    class SimpleRunnable:
        def invoke(self, _input):
            response = llm.invoke([HumanMessage(content=context)])
            text = getattr(response, "content", None)
            if not text:
                gens = getattr(response, "generations", None)
                if gens and len(gens) > 0:
                    text = getattr(gens[0], "text", None) or getattr(getattr(gens[0], "message", None), "content", None)
            try:
                return JobMatchResponse.model_validate_json(text)
            except Exception:
                return JobMatchResponse(
                    match_score=0,
                    matched_skills=[],
                    missing_required_skills=[],
                    missing_preferred_skills=[],
                    keyword_gaps=[],
                    recommendations=[],
                    summary=str(text or ""),
                )

    return SimpleRunnable()
