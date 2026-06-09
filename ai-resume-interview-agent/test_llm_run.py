from dotenv import load_dotenv
load_dotenv()

from llm_provider import get_llm
from chains.ats_chain import analyze_resume_chain

print("Initializing LLM (may download model if missing)...")
llm = get_llm()
print("LLM object:", type(llm))

sample = (
    "Experienced software engineer with 7 years building backend services in Python. "
    "Skilled with Docker, AWS (EC2, S3, RDS), REST APIs, SQL, Redis, and CI/CD pipelines."
)

chain = analyze_resume_chain(sample, llm)
print("Invoking chain (this may take a while if the model downloads)...")
res = chain.invoke({})
print("Invocation finished.")

if isinstance(res, dict):
    print("Result keys:", list(res.keys()))
    ats = res.get("ats")
    if ats:
        try:
            print("ATS score:", ats.ats_score)
        except Exception:
            print("ATS object repr:", repr(ats))
    else:
        print(repr(res))
else:
    print("Result type:", type(res))
    print(repr(res))
