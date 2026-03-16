import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
from email.message import EmailMessage
import smtplib
from github import Github
import openai
import time

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
if "learner_name" not in st.session_state:
    st.session_state.learner_name = ""
if "learner_tag" not in st.session_state:
    st.session_state.learner_tag = ""

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
    st.session_state.learner_name = st.text_input("Enter your name")
    st.session_state.learner_tag = st.text_input("Enter your teacher's number tag")
    
    if st.session_state.learner_name and st.session_state.learner_tag:
        st.success(f"Welcome {st.session_state.learner_name}!")

        # -------------------------
        # CHAT WITH TEACHER
        # -------------------------
        teacher_username = st.text_input("Enter the teacher's username to chat")
        chat_file = f"messages/{teacher_username}_{st.session_state.learner_name}.json"

        if os.path.exists(chat_file):
            with open(chat_file) as f:
                chat_data = json.load(f)
        else:
            chat_data = []

        st.subheader("Chat")
        for msg in chat_data:
            st.write(f"{msg['sender']}: {msg['message']}")

        new_message = st.text_input("Type your message")
        if st.button("Send Message"):
            chat_data.append({"sender": st.session_state.learner_name, "message": new_message})
            with open(chat_file, "w") as f:
                json.dump(chat_data, f)
            st.experimental_rerun()

        # -------------------------
        # TOPICS
        # -------------------------
        default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
        dynamic_topics = [os.path.basename(f).replace(".py", "").replace("_", " ") for f in glob.glob("topics/*.py")]
        topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

        if topic == "LCM & GCD":
            st.subheader("LCM & GCD Visualizer")
            a = st.number_input("Number A",1,50,6)
            b = st.number_input("Number B",1,50,8)
            gcd = math.gcd(a,b)
            lcm = a*b//gcd
            st.success(f"GCD = {gcd}")
            st.success(f"LCM = {lcm}")

            factors_a = [i for i in range(1,a+1) if a%i==0]
            factors_b = [i for i in range(1,b+1) if b%i==0]
            multiples_a = [a*i for i in range(1,10)]
            multiples_b = [b*i for i in range(1,10)]

            fig, ax = plt.subplots()
            y_positions = [1,2,3,4]
            ax.scatter(factors_a,[y_positions[0]]*len(factors_a), color="orange", label="Factors A")
            ax.scatter(factors_b,[y_positions[1]]*len(factors_b), color="blue", label="Factors B")
            ax.scatter(multiples_a,[y_positions[2]]*len(multiples_a), color="green", label="Multiples A")
            ax.scatter(multiples_b,[y_positions[3]]*len(multiples_b), color="red", label="Multiples B")
            ax.scatter(lcm,2.5, s=120, color="purple", label="LCM")
            ax.scatter(gcd,0.5, s=120, color="black", label="GCD")
            ax.set_yticks([0.5,1,2,3,4,2.5])
            ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        elif topic in dynamic_topics:
            file_path = f"topics/{topic.replace(' ','_')}.py"
            with open(file_path) as f:
                exec(f.read())

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_tag = st.text_input("Number tag for learners")
    
    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE, "w") as f:
                json.dump(teacher_data, f)
            st.success("Registered successfully!")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username] == password:
            st.success("Login successful!")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        else:
            st.error("Incorrect password.")

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Description")
        if st.button("Submit Topic for Approval"):
            submission = {
                "teacher": st.session_state.teacher_name,
                "teacher_tag": teacher_tag,
                "topic_name": topic_name,
                "topic_description": topic_description,
                "topic_code": ""
            }
            filename = topic_name.replace(" ","_")+".json"
            with open(f"submissions/{filename}","w") as f:
                json.dump(submission,f)
            st.success("Topic submitted for editor approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard (Password Protected)")
    editor_password_input = st.text_input("Enter editor password", type="password")
    EDITOR_SECRET_PASSWORD = "mercypaul"

    if editor_password_input == EDITOR_SECRET_PASSWORD:
        st.success("Access granted!")

        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")

        if submissions:
            for file in submissions:
                with open(file) as f:
                    data = json.load(f)

                st.subheader(data["topic_name"])
                st.write("Teacher:", data["teacher"])
                st.write("Description:", data["topic_description"])
                st.code(data["topic_code"])

                if st.button(f"Generate Python Code for {data['topic_name']}", key=f"gen{file}"):
                    openai.api_key = st.secrets["OPENAI_API_KEY"]
                    prompt = f"Generate Python code for this topic description:\n{data['topic_description']}"
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role":"user","content":prompt}],
                        temperature=0.5
                    )
                    generated_code = response['choices'][0]['message']['content']
                    st.code(generated_code)
                    data['topic_code'] = generated_code

                if st.button(f"Approve & Push {data['topic_name']}", key=f"push{file}"):
                    try:
                        g = Github(st.secrets["GITHUB_TOKEN"])
                        repo = g.get_repo(repo_name)
                        filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                        repo.create_file(filename,"Add topic",data['topic_code'])
                        os.rename(file,f"approved/{os.path.basename(file)}")
                        st.success("Topic approved, pushed to GitHub!")
                    except Exception as e:
                        st.error(e)
        else:
            st.info("No submissions yet.")

        # Embedded game
        st.subheader("Play Your 3D Game")
        st.components.v1.iframe("https://www.hero-wars.com/?hl=en", width=900, height=600, scrolling=True)
    else:
        st.warning("Enter correct editor password to access this page.")
