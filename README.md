# AI Study Companion Agent

A beginner-friendly, rule-based Agentic AI assignment project built with Python and Streamlit. It runs locally without a paid API key.

## Features

- **Study Planner:** creates a simple revision plan from topics, exam date, and daily study hours.
- **Practice Quiz:** generates a five-question quiz from a built-in question bank.
- **Answer Evaluation:** calculates quiz score and displays explanations.
- **Agent Decision Loop:** recommends `REVISE`, `PRACTISE`, or `ADVANCE` based on quiz performance.
- **Progress Dashboard:** shows attempts, overall accuracy, and the weakest topic during the current session.
- **CSV Export:** downloads the generated study plan.

## How it qualifies as an agent

The system receives observations (topic selection and answers), evaluates the student's performance, chooses an action using an explicit decision policy, and provides the action as feedback. The student can repeat the cycle, allowing recommendations to change based on new results.

Decision policy:
- Score < 60%: REVISE
- Score from 60% to 79%: PRACTISE
- Score >= 80%: ADVANCE

This is a transparent rule-based agent, not an LLM-powered autonomous agent. It does not require an API key. State is held in the Streamlit session and is cleared when the session resets.

## Project structure

```text
ai-study-companion-agent/
├── app.py
├── requirements.txt
├── README.md
├── schema.md
├── .gitignore
└── data/
    └── questions.json
```

## Setup (Windows)

1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/
   - During installation, tick **Add Python to PATH**.
2. Extract the ZIP file.
3. Open the extracted `ai_study_companion_agent` folder.
4. Click the File Explorer address bar, type `cmd`, and press Enter.
5. Create a virtual environment:

   ```bash
   py -m venv .venv
   ```

6. Activate it:

   ```bash
   .venv\Scripts\activate
   ```

7. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

8. Run the app:

   ```bash
   streamlit run app.py
   ```

9. A browser tab should open automatically. If not, copy the local URL printed in the terminal (usually `http://localhost:8501`).

## Quick test checklist

1. **Planner:** keep the sample topics, choose an exam date a few days ahead, set 3 hours/day, and click Generate study plan. Confirm a table appears and the CSV button downloads a file.
2. **Quiz:** select AI Search Algorithms, click Start / reset quiz, answer the five questions, and submit.
3. **Agent:** score below 60% and verify the recommendation says REVISE; score 60–79% and verify PRACTISE; score 80% or above and verify ADVANCE. You may need multiple attempts to test each threshold.
4. **Progress:** verify the attempt count, accuracy, and topic performance update after submissions.
5. **Reset:** click Clear progress and confirm the dashboard empties.

## GitHub publishing

1. Sign in at https://github.com/ and create a **new public repository** named `ai-study-companion-agent`.
2. Do not initialize it with a README if you plan to push this folder as-is.
3. In Command Prompt, from this project folder, run:

   ```bash
   git init
   git add .
   git commit -m "Build AI Study Companion Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/ai-study-companion-agent.git
   git push -u origin main
   ```

4. Replace `YOUR-USERNAME` with your GitHub username. If Git is not installed, install it from https://git-scm.com/downloads and reopen Command Prompt.
5. If GitHub asks you to authenticate, follow its browser sign-in flow. Do not put passwords or access tokens in source code.
6. Copy your repository URL and submit it to your professor.

## Optional live hosting with Streamlit Community Cloud

1. Push the repository to GitHub first.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create an app, select your repository, branch `main`, and main file path `app.py`.
4. Deploy and test the public URL in a private/incognito window.

## Limitations and future improvements

- Small educational question bank; expand `data/questions.json` to add topics and questions.
- Planner uses a simple scheduling rule rather than an optimization algorithm.
- Progress is session-only, not stored permanently.
- No external LLM is used, so question generation is selection from a curated bank rather than free-form generation.

## Academic integrity / explanation

Be prepared to explain the decision policy, how the score is calculated, and the difference between this rule-based agent and a general-purpose LLM chatbot. Run the app yourself and personalize the question bank or topics before submission.
