import streamlit as st
from langchain_core.runnables import RunnableParallel
from services.pdf_parser import extract_pdf_text
from services.resume_extractor import clean_resume_text
from chains.ats_chain import analyze_resume_chain
from chains.skill_chain import extract_skills_from_resume_chain
from chains.job_match_chain import analyze_job_match_chain
from chains.interview_chain import generate_question_chain
from chains.evaluation_chain import evaluate_answer_chain
from chains.rewrite_chain import rewrite_resume_chain
from chains.format_chain import format_resume_chain

import os
from dotenv import load_dotenv
from llm_provider import get_llm

load_dotenv()

# Get an LLM: Gemma via Google GenAI if configured, otherwise a free local fallback
llm = get_llm()

SECTIONS = ["ATS Analysis", "Skills", "Job Match", "Interview", "Rewrite Resume"]

for key in ("resume_text", "ats", "skills", "source_file","current_question", 
        "latest_evaluation", "rewritten_resume", "html_resume", "job_description",
        "job_match"):
    st.session_state.setdefault(key, None)
for key in ("questions", "answers", "evaluations"):
    st.session_state.setdefault(key, [])
if "total_score" not in st.session_state:
    st.session_state.total_score = 0


def run_analysis(cleaned_text: str):
    ats_chain = analyze_resume_chain(cleaned_text, llm)
    skill_chain = extract_skills_from_resume_chain(cleaned_text, llm)
    parallel_chain = RunnableParallel(ats=ats_chain, skills=skill_chain)
    return parallel_chain.invoke({})


def render_ats(ats):
    st.header("ATS Analysis")
    st.metric("ATS Score", ats.ats_score)

    st.subheader("Strengths")
    for item in ats.strengths:
        st.write(f"✅ {item}")

    st.subheader("Weaknesses")
    for item in ats.weaknesses:
        st.write(f"❌ {item}")

    st.subheader("Missing Keywords")
    for item in ats.missing_keywords:
        st.write(f"⚠️ {item}")

    st.subheader("Improvements")
    for item in ats.improvements:
        st.write(f"💡 {item}")

    st.subheader("Summary")
    st.write(ats.summary)


def render_skills(skills_result):
    st.header("Skills Overview")

    if skills_result.candidate_name:
        st.markdown(f"**Candidate:** {skills_result.candidate_name}")
    if skills_result.target_role:
        st.markdown(f"**Target Role:** {skills_result.target_role}")

    st.subheader("Profile Summary")
    st.write(skills_result.extraction_summary)

    st.subheader("Skills by Category")
    skill_groups = {
        "Programming Languages": skills_result.skills.programming_languages,
        "Frameworks & Libraries": skills_result.skills.frameworks_and_libraries,
        "Databases": skills_result.skills.databases,
        "Cloud & DevOps": skills_result.skills.cloud_and_devops,
        "Tools & Platforms": skills_result.skills.tools_and_platforms,
        "AI & ML": skills_result.skills.ai_and_ml,
        "Domains & Concepts": skills_result.skills.domains_and_concepts,
        "APIs & Protocols": skills_result.skills.apis_and_protocols,
    }
    for group_name, items in skill_groups.items():
        if not items:
            continue
        with st.expander(f"{group_name} ({len(items)})"):
            for skill in items:
                st.markdown(
                    f"- **{skill.name}** — "
                    f"`{skill.confidence.value}` · `{skill.proficiency_signal.value}`  \n"
                    f"  _{skill.evidence}_"
                )

    if skills_result.interview_focus_areas:
        st.subheader("Interview Focus Areas")
        for focus in skills_result.interview_focus_areas:
            st.markdown(
                f"🎯 **{focus.skill}** (`{focus.suggested_depth.value}`)  \n"
                f"{focus.reason}"
            )

    if skills_result.skills_flat_list:
        st.subheader("All Skills")
        st.markdown(" ".join(f"`{s}`" for s in skills_result.skills_flat_list))


def render_job_match():
    st.header("Job Match")

    job_description = st.text_area(
        "Paste Job Description",
        value=st.session_state.job_description or "",
        height=260,
        placeholder="Paste the target job description here...",
    )

    if st.button("Find Missing Skills"):
        if not job_description.strip():
            st.warning("Please paste a job description first.")
            return

        st.session_state.job_description = job_description
        with st.spinner("Comparing resume against job description..."):
            try:
                st.session_state.job_match = analyze_job_match_chain(
                    resume_text=st.session_state.resume_text,
                    job_description=job_description,
                    llm=llm,
                ).invoke({})
            except Exception as e:
                st.error("Job match analysis failed. Please verify your Gemini API key, quota, and network connectivity.")
                st.error(str(e))
                return

    match = st.session_state.job_match
    if not match:
        st.info("Paste a job description to see resume-specific missing skills and ATS keyword gaps.")
        return

    st.metric("Job Match Score", f"{match.match_score}/100")
    st.subheader("Summary")
    st.write(match.summary)

    if match.matched_skills:
        st.subheader("Matched Skills")
        st.markdown(" ".join(f"`{skill}`" for skill in match.matched_skills))

    if match.missing_required_skills:
        st.subheader("Missing Required Skills")
        for gap in match.missing_required_skills:
            st.markdown(f"**{gap.skill}**")
            st.write(gap.importance)
            st.caption(f"Job evidence: {gap.evidence_from_job}")
            st.caption(f"Where to add if truthful: {gap.suggested_resume_location}")

    if match.missing_preferred_skills:
        st.subheader("Missing Preferred Skills")
        for gap in match.missing_preferred_skills:
            st.markdown(f"**{gap.skill}**")
            st.write(gap.importance)
            st.caption(f"Job evidence: {gap.evidence_from_job}")
            st.caption(f"Where to add if truthful: {gap.suggested_resume_location}")

    if match.keyword_gaps:
        st.subheader("ATS Keyword Gaps")
        st.markdown(" ".join(f"`{keyword}`" for keyword in match.keyword_gaps))

    if match.recommendations:
        st.subheader("Recommendations")
        for item in match.recommendations:
            st.write(f"- {item}")


def render_result(evaluation):
    st.divider()
    st.subheader("Evaluation")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Overall", f"{evaluation.overall_score}/10")

    with col2:
        st.metric( "Technical", f"{evaluation.technical_accuracy}/10")

    with col3:
        st.metric("Clarity", f"{evaluation.clarity}/10")

    st.write("### Strengths")
    for item in evaluation.strengths:
        st.write(f"✅ {item}")

    st.write("### Weaknesses")
    for item in evaluation.weaknesses:
        st.write(f"❌ {item}")

    st.write("### Improvements")
    for item in evaluation.improvements:
        st.write(f"💡 {item}")

    st.write("### Ideal Answer")
    st.info(evaluation.ideal_answer)

def render_progress_metrics():
    completed = len(st.session_state.answers)
    avg_score = (st.session_state.total_score / completed if completed > 0 else 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Completed", completed)

    with col2:
        st.metric("Average Score", round(avg_score, 1))

    with col3:
        st.metric("Total Score",st.session_state.total_score)

    progress = min(completed / 10, 1.0)
    st.progress(progress)

def render_questions_history():
    with st.expander("Interview History"):
        for i, (q, a, e) in enumerate(
            zip(
                st.session_state.questions,
                st.session_state.answers,
                st.session_state.evaluations
            )
        ):
            st.write(f"### Question {i+1}")
            st.write(q.question)
            st.write("**Your Answer:**")
            st.write(a)
            st.write(f"Score: {e.overall_score}/10")

            st.divider()

def render_questions():
    st.header("Mock Interview")
    render_progress_metrics()
    st.divider()

    if st.button("Start Mock Interview"):
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.evaluations = []
        st.session_state.total_score = 0

        question = generate_question_chain(name=st.session_state.skills.candidate_name,
                role=st.session_state.skills.target_role,
                skills=st.session_state.skills.skills_flat_list,
                previous_questions=[],
                llm=llm).invoke({})
        st.session_state.current_question = question
        st.session_state.questions.append(question)

    if st.session_state.current_question:
        question = st.session_state.current_question
        st.subheader(f"Question ({question.difficulty})")
        st.info(question.question)

        answer = st.text_area("Your Answer")
        if st.button("Submit Answer"):
            evaluation = evaluate_answer_chain(question=st.session_state.current_question,
                answer=answer,
                difficulty=st.session_state.current_question.difficulty,
                llm=llm
            ).invoke({})

            st.session_state.answers.append(answer)
            st.session_state.evaluations.append(evaluation)
            st.session_state.total_score += evaluation.overall_score

            next_question = generate_question_chain(
                name=st.session_state.skills.candidate_name,
                role=st.session_state.skills.target_role,
                skills=st.session_state.skills.skills_flat_list,
                previous_questions=st.session_state.questions,
                llm=llm
            ).invoke({})
            st.session_state.current_question = next_question
            st.session_state.questions.append(next_question)
            st.session_state.latest_evaluation = evaluation

            st.rerun()

    if ("latest_evaluation" in st.session_state and st.session_state.latest_evaluation):
        render_result(st.session_state.latest_evaluation)

def render_rewrite_resume():
    job_role = st.text_input("Enter Job Role")
    job_description = st.text_area("Enter Job Description")

    if st.button("Rewrite Resume"):
        if job_role and job_description:
            rewritten_resume = rewrite_resume_chain(
                resume=st.session_state.resume_text,
                ats=st.session_state.ats,
                skills=st.session_state.skills.skills_flat_list,
                job_role=job_role,
                job_description=job_description,
                llm=llm
            ).invoke({})
            st.session_state.rewritten_resume = rewritten_resume  # ← fix key name too
            st.session_state.html_resume = None                   # reset on new rewrite
        else:
            st.warning("Please fill in both fields.")

    if st.session_state.get("rewritten_resume"):
        st.markdown(st.session_state.rewritten_resume)

        if st.button("Format Resume"):
            html_resume = format_resume_chain(st.session_state.rewritten_resume)
            st.session_state.html_resume = html_resume

    if st.session_state.get("html_resume"):
        st.components.v1.html(st.session_state.html_resume, height=1100, scrolling=True)
        st.download_button(
            label="⬇️ Download Resume (.html)",
            data=st.session_state.html_resume,
            file_name=f"{st.session_state.rewritten_resume.contact.name.replace(' ', '_')}_resume.html",
            mime="text/html",
        )

def main():
    st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

    with st.sidebar:
        st.title("AI Resume Analyzer")
        uploaded_file = st.file_uploader("Upload a pdf file", type=["pdf"])

        if uploaded_file and uploaded_file.name != st.session_state.source_file:
            with st.spinner("Extracting Resume..."):
                raw_text = extract_pdf_text(uploaded_file)
                cleaned_text = clean_resume_text(raw_text)
            if not cleaned_text:
                st.error("Could not extract text from PDF")
                return
            st.session_state.resume_text = cleaned_text
            st.session_state.source_file = uploaded_file.name
            with st.spinner("Analyzing Resume..."):
                try:
                    result = run_analysis(cleaned_text)
                    st.session_state.ats = result["ats"]
                    st.session_state.skills = result["skills"]
                    st.success("Analysis complete")
                except Exception as e:
                    st.error("Resume analysis failed. Please verify your Gemini API key, quota, and network connectivity.")
                    st.error(str(e))
                    return

        section = st.radio("Section", SECTIONS, disabled=st.session_state.ats is None)

    if st.session_state.ats is None:
        st.title("AI Resume ATS Analyzer")
        st.info("Upload a PDF resume from the sidebar to get started.")
        return

    if section == "ATS Analysis":
        render_ats(st.session_state.ats)
    elif section == "Skills":
        render_skills(st.session_state.skills)
    elif section == "Job Match":
        render_job_match()
    elif section == "Interview":
        render_questions()
    elif section == "Rewrite Resume":
        render_rewrite_resume()


main()
