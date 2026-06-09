import os

PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ats_prompt():
    with open(os.path.join(PROMPT_DIR, "ats_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()

def get_skills_prompt():
    with open(os.path.join(PROMPT_DIR, "skills_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()

def get_interview_prompt():
    with open(os.path.join(PROMPT_DIR, "interview_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()

def get_evaluation_prompt():
    with open(os.path.join(PROMPT_DIR, "evaluation_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()

def get_rewrite_prompt():
    with open(os.path.join(PROMPT_DIR, "rewrite_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()

def get_format_prompt():
    with open(os.path.join(PROMPT_DIR, "format_prompt.md"), encoding="utf-8", errors="replace") as file:
        return file.read()