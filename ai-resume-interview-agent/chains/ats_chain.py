from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List

from prompts.prompt_reader import get_ats_prompt

class ATSResponse(BaseModel):
    ats_score: int
    strengths: List[str]
    weaknesses: List[str]
    missing_keywords: List[str]
    improvements: List[str]
    summary: str


def create_context(resume):
    return f"""
    System Prompt : {get_ats_prompt()}
    Resume : {resume}
    """

def analyze_resume_chain(resume_text: str, llm):
    context = create_context(resume_text)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    # If the LLM supports structured output natively, keep original behavior
    try:
        structured_llm = llm.with_structured_output(ATSResponse)
    except NotImplementedError:
        structured_llm = None
    except Exception:
        structured_llm = None

    if structured_llm is not None:
        chain = prompt | structured_llm
        return chain

    # Fallback for local or lightweight LLMs: call the model and parse JSON
    from langchain_core.messages import HumanMessage

    class SimpleRunnable:
        def invoke(self, _input):
            messages = [HumanMessage(content=context)]
            response = llm.invoke(messages)
            # attempt to extract text from response
            text = getattr(response, "content", None)
            if not text:
                gens = getattr(response, "generations", None)
                if gens and len(gens) > 0:
                    text = getattr(gens[0], "text", None) or getattr(getattr(gens[0], 'message', None), 'content', None)
            # Try to parse JSON into ATSResponse, otherwise return a minimal model
            try:
                return ATSResponse.model_validate_json(text)
            except Exception:
                return ATSResponse(ats_score=0, strengths=[], weaknesses=[], missing_keywords=[], improvements=[], summary=str(text or ""))

    return SimpleRunnable()