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
from datetime import datetime

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
os.makedirs("chat", exist_ok=True)  # folder to store chat logs

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "learner_name" not in st.session_state:
    st.session_state.learner_name = ""
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False

# -------------------------
# PASSWORD FILE
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")

    # Login
    learner_username = st.text_input("Enter your username with teacher code (e.g., Alana-42)")
    if st.button("Login as Learner") and learner_username:
        st.session_state.learner_name = learner_username
        st.success(f"Logged in as {learner_username}")

    # Topic Explorer
    if st.session_state.learner_name:
        default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
        dynamic_topics = [os.path.basename(f).replace(".py","").replace("_"," ") for f in glob.glob("topics/*.py")]
        topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

        if topic == "LCM & GCD":
            st.subheader("LCM & GCD Visualizer")
            a = st.number_input("Number A",1,100,6)
            b = st.number_input("Number B",1,100,8)
            gcd = math.gcd(a,b)
            lcm = a*b//gcd
            st.success(f"GCD = {gcd}, LCM = {lcm}")

            factors_a = [i for i in range(1,a+1) if a%i==0]
            factors_b = [i for i in range(1,b+1) if b%i==0]
            multiples_a = [a*i for i in range(1,10)]
            multiples_b = [b*i for i in range(1,10)]

            fig, ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a))
            ax.scatter(factors_b,[2]*len(factors_b))
            ax.scatter(multiples_a,[3]*len(multiples_a))
            ax.scatter(multiples_b,[4]*len(multiples_b))
            ax.scatter(gcd,0.5,s=150)
            ax.scatter(lcm,2.5,s=150)
            ax.set_yticks([0.5,1,2,3,4,2.5])
            ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
            ax.grid(True)
            st.pyplot(fig)

        elif topic in dynamic_topics:
            file_path=f"topics/{topic.replace(' ','_')}.py"
            with open(file_path) as f:
                exec(f.read())

        # -----------------------------
        # Learner-Teacher Chat
        # -----------------------------
        st.subheader("Chat with Teacher")
        chat_code = learner_username.split("-")[-1]
        chat_files = glob.glob("chat/*.json")
        for chat_file in chat_files:
            with open(chat_file) as f:
                chat_data = json.load(f)
            if chat_data["code"] == chat_code:
                for msg in chat_data["messages"]:
                    st.write(f"{msg['sender']} ({msg['time']}): {msg['text']}")

        msg_text = st.text_input("Type your message:")
        if st.button("Send Message") and msg_text:
            chat_file_path = f"chat/chat_{chat_code}.json"
            if os.path.exists(chat_file_path):
                with open(chat_file_path) as f:
                    chat_data = json.load(f)
            else:
                chat_data = {"code": chat_code, "messages":[]}
            chat_data["messages"].append({
                "sender": learner_username,
                "text": msg_text,
                "time": datetime.now().strftime("%H:%M")
            })
            with open(chat_file_path,"w") as f:
                json.dump(chat_data,f)
            st.experimental_rerun()

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")

    teacher_username = st.text_input("Username with code (e.g., MsJane-42)")
    teacher_password = st.text_input("Password", type="password")
    if st.button("Login/Register Teacher") and teacher_username and teacher_password:
        # Register or login
        if teacher_username not in teacher_data:
            teacher_data[teacher_username] = teacher_password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name = teacher_username
            st.success("Registered and logged in!")
        elif teacher_data[teacher_username] == teacher_password:
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name = teacher_username
            st.success("Login successful!")
        else:
            st.error("Incorrect password")

    # Topic submission
    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic for Approval")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        topic_code = st.text_area("Python Code")

        if st.button("Submit Topic") and topic_name:
            filename = f"submissions/{topic_name.replace(' ','_')}.json"
            with open(filename,"w") as f:
                json.dump({
                    "teacher": st.session_state.teacher_name,
                    "topic_name": topic_name,
                    "topic_description": topic_description,
                    "topic_code": topic_code
                }, f)
            st.success("Topic submitted for editor approval!")

        # -----------------------------
        # Teacher-learner chat
        # -----------------------------
        st.subheader("Chat with Learners")
        chat_code = teacher_username.split("-")[-1]
        chat_file_path = f"chat/chat_{chat_code}.json"
        if os.path.exists(chat_file_path):
            with open(chat_file_path) as f:
                chat_data = json.load(f)
            for msg in chat_data["messages"]:
                st.write(f"{msg['sender']} ({msg['time']}): {msg['text']}")
        msg_text = st.text_input("Type your message to learners:")
        if st.button("Send Message to Learners") and msg_text:
            with open(chat_file_path) as f:
                chat_data = json.load(f)
            chat_data["messages"].append({
                "sender": teacher_username,
                "text": msg_text,
                "time": datetime.now().strftime("%H:%M")
            })
            with open(chat_file_path,"w") as f:
                json.dump(chat_data,f)
            st.experimental_rerun()

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard")
    editor_pass = st.text_input("Enter editor password", type="password")
    if st.button("Login Editor") and editor_pass=="mercypaul":
        st.session_state.editor_logged_in=True
        st.success("Editor logged in!")

    if st.session_state.editor_logged_in:
        # AI topic generator
        st.subheader("Generate Python Code from Topic Description")
        topic_desc = st.text_area("Topic Description")
        if st.button("Generate Code") and topic_desc:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Write Python code to demonstrate the math topic: {topic_desc}",
                max_tokens=500
            )
            st.code(response.choices[0].text)

        # GitHub push
        st.subheader("Approve teacher topics & push to GitHub")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.subheader(data["topic_name"])
            st.write("Teacher:", data["teacher"])
            st.write("Description:", data["topic_description"])
            st.code(data["topic_code"])
            if st.button(f"Approve {data['topic_name']}", key=file):
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    repo.create_file(filename, "Add topic", data["topic_code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)

        # Editor private 3D game (placeholder)
        st.subheader("Editor 3D Game")
        st.write("Access granted only to editor. [Game placeholder here]")
