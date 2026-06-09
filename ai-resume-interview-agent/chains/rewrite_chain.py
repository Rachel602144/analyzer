from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_reader import get_rewrite_prompt


class ContactInfo(BaseModel):
    name:      str
    email:     Optional[str] = None
    phone:     Optional[str] = None
    linkedin:  Optional[str] = None
    github:    Optional[str] = None
    location:  Optional[str] = None


class SkillsSection(BaseModel):
    programming_languages:    List[str] = Field(default_factory=list)
    frameworks_and_libraries: List[str] = Field(default_factory=list)
    databases:                List[str] = Field(default_factory=list)
    cloud_and_devops:         List[str] = Field(default_factory=list)
    ai_and_ml:                List[str] = Field(default_factory=list)
    tools_and_platforms:      List[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    job_title:  str
    company:    str
    start_date: str                 # MM/YYYY
    end_date:   str                 # MM/YYYY or "Present"
    location:   Optional[str] = None
    bullets:    List[str]           # rewritten action-verb bullet points


class ProjectEntry(BaseModel):
    name:         str
    technologies: List[str]
    bullets:      List[str]


class EducationEntry(BaseModel):
    degree:      str
    institution: str
    start_year:  Optional[str] = None
    end_year:    str


class Certification(BaseModel):
    name:         str
    issuing_body: Optional[str] = None
    year:         Optional[str] = None


class RewrittenResume(BaseModel):
    contact:        ContactInfo
    summary:        str
    skills:         SkillsSection
    experience:     List[ExperienceEntry]
    projects:       List[ProjectEntry]   = Field(default_factory=list)
    education:      List[EducationEntry]
    certifications: List[Certification]  = Field(default_factory=list)

def create_context(resume, ats, skills, job_role, job_description):
    return f"""
    System Prompt : {get_rewrite_prompt()}
    Original Resume: {resume}
    ATS Analysis: {ats}
    Skills: {skills}
    Job Role Seeking: {job_role}
    Job Description: {job_description}
    """

def rewrite_resume_chain(resume, ats, skills, job_role, job_description, llm):
    context = create_context(resume, ats, skills, job_role, job_description)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    structured_llm = llm.with_structured_output(RewrittenResume)
    chain = prompt | structured_llm

    return chain