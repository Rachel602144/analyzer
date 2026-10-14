# AI Resume Analyzer & Interview Agent

An AI-powered application designed to analyze resumes, evaluate alignment with job descriptions, identify skill gaps, conduct mock interviews, and generate tailored resume content using Large Language Models (LLMs).

## Overview

Preparing for technical interviews and tailoring a resume to a specific job description can involve significant manual effort. This project brings several career preparation workflows together into one Python application.

The system processes resume documents, extracts relevant information, evaluates job alignment, generates interview questions, assesses candidate answers, and helps rewrite resume content for a target role.

The application uses modular LangChain components, structured outputs, and LLM-powered processing to organize these tasks into separate workflows.

## Features

### 1. Resume Analysis

- Extract information from uploaded PDF resumes.
- Analyze resume content using an LLM.
- Identify strengths and areas that need improvement.
- Generate structured feedback to support resume refinement.

### 2. Skill Extraction

- Extract skills mentioned in resume content.
- Organize skills into categories.
- Identify supporting evidence from the resume.
- Highlight areas that may require further interview preparation.

### 3. Job Description Matching

- Compare resume content with a target job description.
- Identify matching skills and potential skill gaps.
- Analyze required and preferred qualifications.
- Generate suggestions for improving alignment with the target role.

### 4. Mock Interview Generation

- Generate interview questions based on the target role and candidate profile.
- Support role-specific interview preparation.
- Evaluate submitted answers using LLM-generated feedback.
- Track interview scores within the application workflow.

### 5. Resume Rewriting

- Generate revised resume content for a target role.
- Incorporate relevant job-description requirements.
- Produce HTML-formatted output for presentation and downloading.
- Help improve clarity and relevance while retaining the candidate's actual experience.

**Important:** Generated resume content should be reviewed for factual accuracy. The system should not be used to invent skills, qualifications, or professional experience.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic and workflow orchestration |
| LangChain | LLM chains, prompt templates, and structured processing |
| Google Gemini | Primary LLM integration |
| Pydantic | Structured output schemas and data validation |
| PyPDF | PDF text extraction |
| Transformers | Local language-model fallback |
| PyTorch | Model execution for the local fallback |
| HTML | Formatting generated resume content |

The project also uses supporting libraries for configuration, data processing, and integration with the selected model provider.

## Architecture

The application separates document processing, prompts, model integration, and career-preparation workflows into different modules.

### 1. Resume Processing

The system extracts text from uploaded PDF documents and prepares the content for downstream analysis.

### 2. LLM Integration

The model integration layer provides access to the configured language model. The project also contains a local Transformers-based fallback.

The primary and fallback models have different capabilities, so output quality and compatibility may vary between them.

### 3. Structured Analysis

Pydantic schemas and LangChain components organize model outputs into structured results for use by the application's workflows.

### 4. Specialized Workflows

Separate chains and modules handle resume analysis, skill extraction, job matching, interview generation, answer evaluation, and resume rewriting.

This modular design makes it easier to maintain and extend individual workflows without placing all the application logic in a single script.

## Project Structure

The repository contains an `ai-resume-interview-agent` application directory. The main application modules are organized around the following responsibilities:

```text
analyzer/
├── README.md
└── ai-resume-interview-agent/
    ├── requirements.txt
    ├── app/
    │   └── ...
    └── ...
```

The directory structure above is illustrative. Refer to the actual repository files for the exact module names and locations.

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the dependencies
- Access to the configured LLM provider
- An API key for the selected model provider
- The Python dependencies listed in `requirements.txt`

### 1. Clone the Repository

```bash
git clone https://github.com/Rachel602144/analyzer.git
cd analyzer
```

Navigate into the application directory:

```bash
cd ai-resume-interview-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Some local model configurations may require additional dependencies. Verify that all imported packages are included in the requirements file before running the application.

### 4. Configure API Credentials

Set the environment variables required by the model integration.

For example, if the application uses Google Gemini:

```env
GOOGLE_API_KEY=your_google_api_key
```

Use the exact environment-variable names expected by the source code. Store credentials in a local `.env` file or your environment, and never commit real API keys to GitHub.

### 5. Run the Application

The exact entry point should be verified against the current application files. Run the script or application command defined by the project rather than assuming a particular framework or entry point.

## Typical Workflow

1. Provide a resume in PDF format.
2. Extract and analyze resume content.
3. Review the identified skills, strengths, and areas for improvement.
4. Supply a target job description for job-alignment analysis.
5. Generate role-specific interview questions.
6. Submit answers for feedback and evaluation.
7. Generate revised resume content and review it before use.

The availability of each workflow depends on the corresponding module and its successful configuration.

## Limitations

- LLM-generated assessments may be inaccurate or inconsistent.
- Resume analysis depends on the quality of extracted PDF text.
- Job matching depends on the completeness of the resume and job description.
- Interview scores are model-generated feedback, not validated measures of candidate ability.
- The local fallback model may produce different results from the primary model.
- The project requires successful configuration of its dependencies and model provider.
- Production readiness and end-to-end execution have not been established by this documentation.

## Future Improvements

- Add a polished, unified user interface.
- Provide downloadable reports for resume analysis and job matching.
- Add automated tests for PDF extraction, structured outputs, and individual workflows.
- Improve error handling for malformed documents and model API failures.
- Add evaluation datasets to measure the consistency of model-generated feedback.
- Make dependency installation reproducible.
- Add sample inputs and outputs using fictional candidate data.
- Improve privacy controls for uploaded resumes and candidate information.

## Security and Privacy

Resumes contain personal information. Treat uploaded documents and model-provider requests accordingly.

- Never commit real API keys or credentials.
- Avoid uploading resumes containing personal information to public repositories.
- Do not include real candidate documents in example data.
- Review the privacy and data-retention policies of any external model provider.
- Validate generated content before using it in applications.

## Author

**Rachel Patni**

- [GitHub Profile](https://github.com/Rachel602144)
- [Project Repository](https://github.com/Rachel602144/analyzer)

---

*This project explores LLM application development, document processing, structured outputs, prompt engineering, and modular AI workflows for resume analysis and interview preparation.*
