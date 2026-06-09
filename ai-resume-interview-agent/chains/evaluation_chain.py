from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prompts.prompt_reader import get_evaluation_prompt


class EvaluationResponse(BaseModel):
    overall_score: int
    technical_accuracy: int
    clarity: int
    completeness: int
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]
    ideal_answer: str

def create_context(question, answer, difficulty):
    return f"""
    System Prompt : {get_evaluation_prompt()}
    Question : {question}
    Answer : {answer}
    Difficulty : {difficulty}
    """

def evaluate_answer_chain(question, answer, difficulty, llm):
    context = create_context(question, answer, difficulty)
    prompt = ChatPromptTemplate.from_messages([("human", context)])
    try:
        structured_llm = llm.with_structured_output(EvaluationResponse)
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
                return EvaluationResponse.model_validate_json(text)
            except Exception:
                return EvaluationResponse(overall_score=0, technical_accuracy=0, clarity=0, completeness=0, strengths=[], weaknesses=[], improvements=[], ideal_answer=str(text or ""))

    return SimpleRunnable()