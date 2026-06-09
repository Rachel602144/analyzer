from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List
from enum import Enum

from prompts.prompt_reader import get_interview_prompt

class Difficulty(str, Enum):
    HARD = "HARD"
    MEDIUM = "MEDIUM"
    EASY = "EASY"


class InterviewQuestion(BaseModel):
    question: str
    difficulty: Difficulty

def create_context(name, role, skills, previous_questions):
    return f"""
    System Prompt : {get_interview_prompt()}
    Name : {name}
    Role : {role}
    Skills : {skills}
    Previous Questions : {previous_questions}
    """

def generate_question_chain(name, role, skills, previous_questions, llm):
    context = create_context(name, role, skills, previous_questions)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    try:
        structured_llm = llm.with_structured_output(InterviewQuestion)
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
                return InterviewQuestion.model_validate_json(text)
            except Exception:
                return InterviewQuestion(question=str(text or ""), difficulty=Difficulty.MEDIUM)

    return SimpleRunnable()