import streamlit as st
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd

# ====================================
# LOAD ENV
# ====================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ====================================
# CLIENTS
# ====================================

client = Groq(
    api_key=GROQ_API_KEY
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ====================================
# PAGE
# ====================================

st.set_page_config(
    page_title="AI Todo List",
    page_icon="✅",
    layout="wide"
)

# ====================================
# COLORFUL UI
# ====================================

st.markdown("""
<style>

.stApp{
background:
linear-gradient(
135deg,
#ff9a9e 0%,
#fad0c4 25%,
#fbc2eb 50%,
#a18cd1 75%,
#84fab0 100%
);
}

.block-container{
background:white;
padding:2rem;
border-radius:20px;
}

.todo-card{
background:#ffffff;
padding:15px;
border-radius:15px;
margin-bottom:10px;
box-shadow:0px 2px 10px rgba(0,0,0,0.1);
}

h1,h2,h3{
color:#1f2937;
}

</style>
""", unsafe_allow_html=True)

# ====================================
# DATABASE FUNCTIONS
# ====================================

def add_task(task, priority, ai_tip):

    supabase.table(
        "todos"
    ).insert({
        "task": task,
        "priority": priority,
        "ai_tip": ai_tip
    }).execute()


def get_tasks():

    result = (
        supabase
        .table("todos")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return result.data


def delete_task(task_id):

    (
        supabase
        .table("todos")
        .delete()
        .eq("id", task_id)
        .execute()
    )


def mark_completed(task_id):

    (
        supabase
        .table("todos")
        .update({
            "status": "Completed"
        })
        .eq("id", task_id)
        .execute()
    )

# ====================================
# HEADER
# ====================================

st.title("🌈 AI Todo List")

st.caption(
    "Groq + Supabase Productivity Manager"
)

# ====================================
# CREATE TASK
# ====================================

st.subheader("➕ Add New Task")

task = st.text_input(
    "Task Name"
)

priority = st.selectbox(
    "Priority",
    [
        "Low",
        "Medium",
        "High"
    ]
)

if st.button("✨ Generate AI Tip"):

    if task:

        prompt = f"""
Task: {task}

Give:
1. Productivity tip
2. Best approach
3. Estimated effort

Maximum 50 words.
"""

        response = (
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        ai_tip = (
            response
            .choices[0]
            .message
            .content
        )

        st.session_state["ai_tip"] = ai_tip

if "ai_tip" in st.session_state:

    st.info(
        st.session_state["ai_tip"]
    )

if st.button("💾 Save Task"):

    if task:

        tip = st.session_state.get(
            "ai_tip",
            ""
        )

        add_task(
            task,
            priority,
            tip
        )

        st.success(
            "Task Added Successfully"
        )

        st.rerun()

# ====================================
# TASKS
# ====================================

st.subheader("📋 Your Tasks")

tasks = get_tasks()

if tasks:

    completed = len(
        [
            t for t in tasks
            if t["status"] == "Completed"
        ]
    )

    progress = completed / len(tasks)

    st.progress(progress)

    st.write(
        f"Completed {completed} of {len(tasks)} Tasks"
    )

    for task in tasks:

        with st.container():

            st.markdown(
                f"""
<div class='todo-card'>
<b>{task['task']}</b>

<br>

Priority:
{task['priority']}

<br>

Status:
{task['status']}
</div>
""",
                unsafe_allow_html=True
            )

            if task["ai_tip"]:

                st.success(
                    task["ai_tip"]
                )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    f"✅ Complete {task['id']}"
                ):

                    mark_completed(
                        task["id"]
                    )

                    st.rerun()

            with col2:

                if st.button(
                    f"🗑 Delete {task['id']}"
                ):

                    delete_task(
                        task["id"]
                    )

                    st.rerun()

else:

    st.info(
        "No Tasks Added Yet"
    )