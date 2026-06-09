# AI Resume Checker & Interview Agent

> A multi-agent system built with LangChain and Streamlit for ATS resume analysis, rewriting, and mock interview preparation.

---

## Overview

This project is a multi-phase AI pipeline that helps job seekers optimize their resumes and prepare for interviews. It combines LangChain's agent framework with a Streamlit UI to deliver an end-to-end career assistant.

---

## Phases

### Phase 1 — ATS Resume Analysis

Parses and evaluates a resume against ATS (Applicant Tracking System) criteria.

- [x] Upload PDF resume
- [x] Extract text from PDF
- [x] Clean extracted text
- [x] Send text to ATS chain
- [x] Generate ATS analysis
- [x] Display results in Streamlit

---

### Phase 2 — Mock Interview

Generates role-specific interview questions and simulates a conversational interview session.

- [x] reads resume
- [x] extracts skills/topics
- [x] generates interview questions
- [x] asks questions interactively
- [x] stores interview state
- [x] supports multiple questions

---

### Phase 3 — Answer Evaluation

Scores and provides feedback on candidate responses.

- [ ] Answer evaluator
- [ ] Scoring system

---

### Phase 4 — Resume Rewriting

Rewrites and tailors the resume for a specific role or job description.

- [ ] Resume rewriting
- [ ] Role targeting

---

## Tech Stack

| Layer     | Technology          |
|-----------|---------------------|
| UI        | Streamlit           |
| AI / LLM  | LangChain           |
| Document  | PDF parsing (PyPDF / pdfplumber) |

---

## Roadmap

- [x] Phase 1: ATS Analysis
- [ ] Phase 2: Mock Interview
- [ ] Phase 3: Answer Evaluation
- [ ] Phase 4: Resume Rewriting