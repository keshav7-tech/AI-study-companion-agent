import json
import random
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
QUESTION_FILE = APP_DIR / "data" / "questions.json"

st.set_page_config(
    page_title="AI Study Companion Agent",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Study Companion Agent")
st.caption("Plan smarter • Practise • Learn from results • Choose the next action")

# A transparent, rule-based agent. No API key or paid service is required.
with QUESTION_FILE.open("r", encoding="utf-8") as file:
    QUESTION_BANK = json.load(file)

if "attempts" not in st.session_state:
    st.session_state.attempts = []
if "study_plan" not in st.session_state:
    st.session_state.study_plan = []
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None


def agent_decision(score_percent, topic, attempts_for_topic):
    """Select the next study action from the latest quiz result."""
    if score_percent < 60:
        return {
            "action": "REVISE",
            "message": f"Your score on **{topic}** was {score_percent}%. Review the core concepts, then retry a short quiz.",
            "reason": "Score below 60%: the topic needs reinforcement before moving forward.",
        }
    if score_percent < 80:
        return {
            "action": "PRACTISE",
            "message": f"You scored {score_percent}% on **{topic}**. Practise a few more questions to strengthen recall.",
            "reason": "Score from 60% to 79%: understanding is developing, but needs more practice.",
        }
    return {
        "action": "ADVANCE",
        "message": f"Nice work! You scored {score_percent}% on **{topic}**. Move to another topic or try a harder set.",
        "reason": "Score of 80% or higher: the topic is ready for progression.",
    }


def make_plan(raw_topics, exam_day, hours_per_day):
    topics = [line.strip() for line in raw_topics.splitlines() if line.strip()]
    if not topics:
        return [], "Enter at least one topic, with one topic per line."
    days_left = (exam_day - date.today()).days + 1
    if days_left < 1:
        return [], "Choose today or a future date for the exam."
    # Reserve the final day for revision when there is more than one day.
    if days_left >= 3:
        learning_days = days_left - 1
    else:
        learning_days = days_left
    sessions = []
    total_slots = max(learning_days, 1)
    for index, topic in enumerate(topics):
        day_offset = index % total_slots
        session_day = date.today() + timedelta(days=day_offset)
        sessions.append({
            "day": session_day.isoformat(),
            "topic": topic,
            "duration": round(hours_per_day / max(1, min(len(topics), total_slots)), 1),
            "task": "Learn concepts + solve practice questions",
        })
    if days_left >= 3:
        sessions.append({
            "day": exam_day.isoformat(),
            "topic": "All topics",
            "duration": hours_per_day,
            "task": "Final revision + redo incorrect questions",
        })
    return sessions, None


tabs = st.tabs(["🗓️ Study Planner", "🧠 Practice Quiz", "📊 Progress & Agent Decision", "ℹ️ How it works"])

with tabs[0]:
    st.subheader("Build a study plan")
    st.write("Enter one topic per line. The planner creates a simple schedule based on your exam date and available study time.")
    topics_text = st.text_area(
        "Subjects / topics",
        value="AI Search Algorithms\nMachine Learning Basics\nNeural Networks",
        height=130,
        help="Example: Thermodynamics, Fluid Mechanics, AI Search Algorithms",
    )
    c1, c2 = st.columns(2)
    with c1:
        exam_date = st.date_input("Exam date", value=date.today() + timedelta(days=3), min_value=date.today())
    with c2:
        hours = st.number_input("Available study hours per day", min_value=0.5, max_value=16.0, value=3.0, step=0.5)
    if st.button("Generate study plan", type="primary"):
        plan, error = make_plan(topics_text, exam_date, hours)
        if error:
            st.error(error)
        else:
            st.session_state.study_plan = plan
            st.success("Study plan generated.")
    if st.session_state.study_plan:
        st.markdown("### Your plan")
        st.dataframe(st.session_state.study_plan, use_container_width=True, hide_index=True)
        plan_csv = "day,topic,duration,task\n" + "\n".join(
            f'{row["day"]},{row["topic"].replace(",", " ")},{row["duration"]},{row["task"]}'
            for row in st.session_state.study_plan
        )
        st.download_button("Download plan as CSV", plan_csv, file_name="study_plan.csv", mime="text/csv")

with tabs[1]:
    st.subheader("Take a practice quiz")
    all_topics = sorted(QUESTION_BANK.keys())
    selected_topic = st.selectbox("Choose a topic", all_topics)
    questions = QUESTION_BANK[selected_topic]
    count = min(5, len(questions))
    if st.button("Start / reset quiz"):
        chosen = random.sample(questions, k=count)
        st.session_state.quiz = {
            "topic": selected_topic,
            "questions": chosen,
            "submitted": False,
        }
        st.session_state.last_feedback = None

    quiz = st.session_state.quiz
    if quiz:
        if quiz["topic"] != selected_topic:
            st.info("The active quiz is for a different topic. Click **Start / reset quiz** to load this topic.")
        else:
            with st.form("quiz_form"):
                answers = {}
                for i, q in enumerate(quiz["questions"]):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    answers[str(i)] = st.radio(
                        "Select one answer",
                        q["options"],
                        key=f"answer_{quiz['topic']}_{i}_{id(quiz)}",
                        index=None,
                        label_visibility="collapsed",
                    )
                submitted = st.form_submit_button("Submit answers", type="primary")
            if submitted:
                correct = 0
                details = []
                for i, q in enumerate(quiz["questions"]):
                    chosen_answer = answers[str(i)]
                    is_correct = chosen_answer == q["answer"]
                    correct += int(is_correct)
                    details.append({
                        "question": q["question"],
                        "your_answer": chosen_answer or "Not answered",
                        "correct_answer": q["answer"],
                        "correct": is_correct,
                        "explanation": q["explanation"],
                    })
                score = round(100 * correct / len(quiz["questions"]))
                decision = agent_decision(score, quiz["topic"], st.session_state.attempts)
                attempt = {
                    "date": date.today().isoformat(),
                    "topic": quiz["topic"],
                    "correct": correct,
                    "total": len(quiz["questions"]),
                    "score": score,
                    "agent_action": decision["action"],
                }
                st.session_state.attempts.append(attempt)
                st.session_state.last_feedback = {"attempt": attempt, "decision": decision, "details": details}
                st.session_state.quiz = None
                st.rerun()

    feedback = st.session_state.last_feedback
    if feedback:
        st.markdown("### Quiz result")
        st.metric("Score", f"{feedback['attempt']['score']}%", f"{feedback['attempt']['correct']} / {feedback['attempt']['total']} correct")
        for i, item in enumerate(feedback["details"], start=1):
            icon = "✅" if item["correct"] else "❌"
            st.markdown(f"{icon} **Q{i}. {item['question']}**")
            st.write(f"Your answer: {item['your_answer']}")
            st.write(f"Correct answer: {item['correct_answer']}")
            st.caption(item["explanation"])
        st.markdown("### Agent recommendation")
        st.write(feedback["decision"]["message"])
        st.caption("Decision logic: " + feedback["decision"]["reason"])

with tabs[2]:
    st.subheader("Progress dashboard")
    attempts = st.session_state.attempts
    if not attempts:
        st.info("No quiz attempts yet. Complete a quiz and the agent will use your score to recommend the next step.")
    else:
        total_correct = sum(a["correct"] for a in attempts)
        total_questions = sum(a["total"] for a in attempts)
        average = round(100 * total_correct / total_questions)
        c1, c2, c3 = st.columns(3)
        c1.metric("Quiz attempts", len(attempts))
        c2.metric("Overall accuracy", f"{average}%")
        c3.metric("Questions answered", total_questions)
        st.dataframe(attempts, use_container_width=True, hide_index=True)
        topic_scores = {}
        for attempt in attempts:
            topic_scores.setdefault(attempt["topic"], []).append(attempt["score"])
        summary = [
            {"topic": topic, "average_score": round(sum(scores) / len(scores)), "attempts": len(scores)}
            for topic, scores in topic_scores.items()
        ]
        st.markdown("### Topic performance")
        st.dataframe(summary, use_container_width=True, hide_index=True)
        weakest = min(summary, key=lambda item: item["average_score"])
        st.warning(f"Agent's current priority: **{weakest['topic']}** (average {weakest['average_score']}%).")
        st.caption("Progress is stored in the current browser session. Restarting the app clears it; persistent storage can be added later.")
    if st.button("Clear progress", type="secondary"):
        st.session_state.attempts = []
        st.session_state.last_feedback = None
        st.session_state.quiz = None
        st.rerun()

with tabs[3]:
    st.subheader("System overview")
    st.markdown("""
**Goal:** help a student plan revision, practise questions, and decide what to do next.

**Agent loop**
1. **Perceive:** read the chosen topic and quiz answers.
2. **Evaluate:** calculate the score and inspect topic performance.
3. **Decide:** apply a transparent policy to choose REVISE, PRACTISE, or ADVANCE.
4. **Act:** display feedback and the next recommended learning action.
5. **Repeat:** the student takes another quiz and the agent updates its recommendation.

**Decision policy**
- Score below 60% → **REVISE**
- Score from 60% to 79% → **PRACTISE**
- Score 80% or higher → **ADVANCE**

This is a lightweight, rule-based agent rather than a large language model. It works without an API key and makes its decisions explainable, which is useful for demonstrating the agent workflow in an academic evaluation.
""")
    st.markdown("**Limitations:** the built-in question bank is small; the study plan uses a simple distribution rule; session progress is not permanent.")
