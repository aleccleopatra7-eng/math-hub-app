import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
import smtplib
from email.message import EmailMessage
from github import Github
import openai
import streamlit.components.v1 as components

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊", layout="centered")
st.title("📊 Interactive Math Hub")

# -------------------------
# CREATE REQUIRED FOLDERS
# -------------------------
os.makedirs("topics", exist_ok=True)
os.makedirs("submissions", exist_ok=True)
os.makedirs("approved", exist_ok=True)
os.makedirs("messages", exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False

# -------------------------
# LOAD TEACHERS
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# Put your editor password here
EDITOR_PASSWORD = "your_editor_password_here"  # <<-- Replace with your editor password

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py", "").replace("_", " ") for f in glob.glob("topics/*.py")]
    
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)
    
    # -------------------------
    # LCM & GCD
    # -------------------------
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)
        gcd = math.gcd(a, b)
        lcm = a * b // gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")
        factors_a = [i for i in range(1, a+1) if a % i == 0]
        factors_b = [i for i in range(1, b+1) if b % i == 0]
        multiples_a = [a * i for i in range(1, 10)]
        multiples_b = [b * i for i in range(1, 10)]

        fig, ax = plt.subplots()
        y_positions = [1, 2, 3, 4]
        ax.scatter(factors_a, [y_positions[0]]*len(factors_a), marker="s", color="orange", label="Factors A")
        ax.scatter(factors_b, [y_positions[1]]*len(factors_b), marker="s", color="blue", label="Factors B")
        ax.scatter(multiples_a, [y_positions[2]]*len(multiples_a), marker="o", color="green", label="Multiples A")
        ax.scatter(multiples_b, [y_positions[3]]*len(multiples_b), marker="o", color="red", label="Multiples B")
        ax.scatter(lcm, 2.5, color="green", s=120, label="LCM")
        ax.scatter(gcd, 0.5, color="orange", s=120, label="GCD")
        for x in factors_a: ax.text(x, 1.05, str(x), ha="center")
        for x in factors_b: ax.text(x, 2.05, str(x), ha="center")
        for x in multiples_a: ax.text(x, 3.05, str(x), ha="center")
        for x in multiples_b: ax.text(x, 4.05, str(x), ha="center")
        ax.set_yticks([0.5, 1, 2, 3, 4, 2.5])
        ax.set_yticklabels(["GCD", "Factors A", "Factors B", "Multiples A", "Multiples B", "LCM"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # Other Topics
    # -------------------------
    elif topic == "Ratios":
        st.header("Ratios")
        a = st.number_input("Value A", 1, 100, 4)
        b = st.number_input("Value B", 1, 100, 6)
        st.write(f"The ratio A:B is {a}:{b}")

    elif topic == "Prime Factors":
        st.header("Prime Factors")
        n = st.number_input("Enter a number", 2, 100, 12)
        factors = []
        temp = n
        for i in range(2, temp+1):
            while temp % i == 0:
                factors.append(i)
                temp = temp // i
        st.write("Prime factors:", factors)

    elif topic == "Simultaneous Equations":
        st.header("Solve 2x2 Simultaneous Equations")
        st.write("Equation format: a1*x + b1*y = c1, a2*x + b2*y = c2")
        a1 = st.number_input("a1", value=1)
        b1 = st.number_input("b1", value=1)
        c1 = st.number_input("c1", value=2)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=1)
        c2 = st.number_input("c2", value=3)
        det = a1*b2 - a2*b1
        if det != 0:
            x = (c1*b2 - c2*b1)/det
            y = (a1*c2 - a2*c1)/det
            st.success(f"x = {x}, y = {y}")
        else:
            st.error("No unique solution exists")

    # -------------------------
    # Learner-Teacher Chat
    # -------------------------
    st.subheader("Chat with Teacher")
    learner_name = st.text_input("Your Name")
    teacher_number = st.text_input("Teacher Number")
    chat_file = f"messages/{teacher_number}.json"
    if os.path.exists(chat_file):
        with open(chat_file) as f:
            chat_history = json.load(f)
    else:
        chat_history = []
    new_message = st.text_input("Type your message")
    if st.button("Send"):
        if learner_name.strip() and new_message.strip():
            chat_history.append({"sender": learner_name, "message": new_message})
            with open(chat_file, "w") as f:
                json.dump(chat_history, f)
            st.experimental_rerun()
    st.write("Messages:")
    for msg in chat_history:
        st.write(f"{msg['sender']}: {msg['message']}")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_number = st.text_input("Your Number Tag (for chat)")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE, "w") as f:
                json.dump(teacher_data, f)
            st.success("Registered successfully")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username] == password:
            st.success("Login successful")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        else:
            st.error("Wrong password")

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic Description")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Description"):
            submission = {
                "teacher": st.session_state.teacher_name,
                "topic_number": teacher_number,
                "topic_name": topic_name,
                "topic_description": topic_description
            }
            filename = f"{topic_name.replace(' ', '_')}.json"
            with open(f"submissions/{filename}", "w") as f:
                json.dump(submission, f)
            st.success("Topic description submitted for editor approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard")
    editor_pass_input = st.text_input("Enter Editor Password", type="password")
    if editor_pass_input == EDITOR_PASSWORD:mercypaul123
        st.session_state.editor_logged_in = True

    if st.session_state.editor_logged_in:
        st.subheader("Approve Topics & Generate Python Code")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.write("Teacher:", data["teacher"])
            st.write("Topic Name:", data["topic_name"])
            st.write("Description:", data["topic_description"])
            st.code(data.get("topic_code", ""))

            if st.button(f"Generate Code for {data['topic_name']}", key=file):
                prompt = f"Generate a Python code snippet for the following topic:\n{data['topic_description']}"
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=500
                )
                generated_code = response.choices[0].text.strip()
                data["topic_code"] = generated_code
                with open(file, "w") as f:
                    json.dump(data, f)
                st.code(generated_code)
                st.success("Code generated!")

            if st.button(f"Approve & Push {data['topic_name']}", key=file+"_push"):
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ', '_')}.py"
                    if os.path.exists(filename):
                        repo.update_file(filename, f"Update topic {data['topic_name']}", data["topic_code"], repo.get_contents(filename).sha)
                    else:
                        repo.create_file(filename, f"Add topic {data['topic_name']}", data["topic_code"])
                    os.rename(file, f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)

        # 3D Game
        st.subheader("Play Your Private 3D Game")
        game_url = "https://www.hero-wars.com/?hl=en"
        st.markdown(f"[Click to play your 3D game]({game_url})")
        components.iframe(game_url, width=1000, height=600)
    else:
        st.info("Enter editor password to access this section.")
