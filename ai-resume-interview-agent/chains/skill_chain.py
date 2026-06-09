from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_reader import get_skills_prompt

# ── Enums ────────────────────────────────────────────────────────────────────

class Confidence(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


class ProficiencySignal(str, Enum):
    PRIMARY   = "PRIMARY"
    SECONDARY = "SECONDARY"
    MENTIONED = "MENTIONED"


class SuggestedDepth(str, Enum):
    CONCEPTUAL = "conceptual"
    PRACTICAL  = "practical"
    DEEP_DIVE  = "deep-dive"


class DatabaseType(str, Enum):
    RELATIONAL  = "relational"
    NOSQL       = "NoSQL"
    VECTOR      = "vector"
    GRAPH       = "graph"
    TIME_SERIES = "time-series"
    CACHE       = "cache"
    OTHER       = "other"


class CloudCategory(str, Enum):
    CLOUD_PROVIDER  = "cloud provider"
    CI_CD           = "CI/CD"
    CONTAINERIZATION = "containerization"
    ORCHESTRATION   = "orchestration"
    MONITORING      = "monitoring"
    IAC             = "IaC"
    OTHER           = "other"


class AICategory(str, Enum):
    FRAMEWORK     = "framework"
    MODEL_TYPE    = "model type"
    TECHNIQUE     = "technique"
    DATA_PIPELINE = "data pipeline"
    MLOPS         = "MLOps"
    OTHER         = "other"


# ── Base Skill ────────────────────────────────────────────────────────────────

class BaseSkill(BaseModel):
    name: str = Field(..., description="Name of the skill, tool, or technology")
    confidence: Confidence = Field(..., description="How certain the extraction is based on resume evidence")
    proficiency_signal: ProficiencySignal = Field(..., description="How deeply the candidate used this skill")
    evidence: str = Field(..., description="Brief quote or reference from the resume supporting this extraction")


# ── Skill Variants ────────────────────────────────────────────────────────────

class ProgrammingLanguage(BaseSkill):
    pass


class FrameworkOrLibrary(BaseSkill):
    pass


class Database(BaseSkill):
    type: DatabaseType = Field(..., description="Type of database system")


class CloudAndDevOps(BaseSkill):
    category: CloudCategory = Field(..., description="Sub-category within cloud and DevOps tooling")


class ToolOrPlatform(BaseSkill):
    pass


class AIAndML(BaseSkill):
    category: AICategory = Field(..., description="Sub-category within AI/ML ecosystem")


class DomainOrConcept(BaseSkill):
    pass


class APIOrProtocol(BaseSkill):
    pass


# ── Skills Container ──────────────────────────────────────────────────────────

class Skills(BaseModel):
    programming_languages:   List[ProgrammingLanguage] = Field(default_factory=list)
    frameworks_and_libraries: List[FrameworkOrLibrary]  = Field(default_factory=list)
    databases:               List[Database]             = Field(default_factory=list)
    cloud_and_devops:        List[CloudAndDevOps]       = Field(default_factory=list)
    tools_and_platforms:     List[ToolOrPlatform]       = Field(default_factory=list)
    ai_and_ml:               List[AIAndML]              = Field(default_factory=list)
    domains_and_concepts:    List[DomainOrConcept]      = Field(default_factory=list)
    apis_and_protocols:      List[APIOrProtocol]        = Field(default_factory=list)


# ── Interview Focus ───────────────────────────────────────────────────────────

class InterviewFocusArea(BaseModel):
    skill:           str            = Field(..., description="Name of the skill to focus on")
    reason:          str            = Field(..., description="Why this skill is a high-priority interview topic")
    suggested_depth: SuggestedDepth = Field(..., description="Recommended depth of questioning for this skill")


# ── Root Model ────────────────────────────────────────────────────────────────

class ResumeSkillExtractionResponse(BaseModel):
    candidate_name:       Optional[str]          = Field(None, description="Full name of the candidate, or null if not found")
    target_role:          Optional[str]          = Field(None, description="Inferred target role from the resume, or null if unclear")
    extraction_summary:   str                    = Field(..., description="2-sentence summary of the candidate's overall technical profile")
    skills:               Skills                 = Field(..., description="All extracted skills grouped by category")
    interview_focus_areas: List[InterviewFocusArea] = Field(..., description="Top 6–8 skills most worth probing in an interview, ranked by centrality")
    skills_flat_list:     List[str]              = Field(..., description="Deduplicated flat list of all extracted skill names for downstream keyword injection")


def create_context(resume):
    return f"""
    System Prompt : {get_skills_prompt()}
    Resume : {resume}
    """

def extract_skills_from_resume_chain(resume_text: str, llm):
    context = create_context(resume_text)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    try:
        structured_llm = llm.with_structured_output(ResumeSkillExtractionResponse)
    except NotImplementedError:
        structured_llm = None
    except Exception:
        structured_llm = None

    if structured_llm is not None:
        chain = prompt | structured_llm
        return chain

    from langchain_core.messages import HumanMessage

    class SimpleRunnable:
        def invoke(self, _input):
            messages = [HumanMessage(content=context)]
            response = llm.invoke(messages)
            text = getattr(response, "content", None)
            if not text:
                gens = getattr(response, "generations", None)
                if gens and len(gens) > 0:
                    text = getattr(gens[0], "text", None) or getattr(getattr(gens[0], 'message', None), 'content', None)
            try:
                return ResumeSkillExtractionResponse.model_validate_json(text)
            except Exception:
                # Return minimal empty structure on parse failure
                return ResumeSkillExtractionResponse(extraction_summary=str(text or ""), skills=Skills(), interview_focus_areas=[], skills_flat_list=[])

    return SimpleRunnable()