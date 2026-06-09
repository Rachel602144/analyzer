import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.prompt_reader import get_format_prompt
from dotenv import load_dotenv
from llm_provider import get_llm

load_dotenv()


def format_resume_chain(resume):
    llm = get_llm()
    system_prompt = get_format_prompt()
    resume_json   = resume.model_dump_json(indent=2)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Generate the HTML resume for the following data:\n\n{resume_json}")
    ]
    # Attempt to allow large outputs when supported by the provider
    try:
        llm.model_kwargs["max_tokens"] = 65000
    except Exception:
        pass
    response = llm.invoke(messages)
    # `response` may be a structured object or plain message depending on LLM
    html_output = getattr(response, 'content', None) or getattr(response, 'generations', [None])[0]

    if hasattr(html_output, 'text'):
        html_output = html_output.text

    if not isinstance(html_output, str):
        html_output = str(html_output)

    if "<!DOCTYPE html>" in html_output:
        html_output = html_output[html_output.index("<!DOCTYPE html>"):]

    return html_output