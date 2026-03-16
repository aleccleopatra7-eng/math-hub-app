import streamlit as st
import os
import glob
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from email.message import EmailMessage
import smtplib
import openai
from github import Github

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊", layout="wide")
st.title("📊 Interactive Math Hub")

# -------------------------
# FOLDERS
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
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "editor_name" not in st.session_state:
    st.session_state.editor_name = ""

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# -------------------------
# PASSWORD FILE (Teachers)
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

    # Built-in topics
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]

    # Dynamic topics from approved
    dynamic_topics = []
    for f in glob.glob("topics/*.py"):
        name = os.path.basename(f).replace(".py","").replace("_"," ")
        dynamic_topics.append(name)

    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    # Built-in: LCM & GCD
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A",1,100,6)
        b = st.number_input("Number B",1,100,8)
        gcd = math.gcd(a,b)
        lcm = a*b//gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")
        factors_a=[i for i in range(1,a+1) if a%i==0]
        factors_b=[i for i in range(1,b+1) if b%i==0]
        multiples_a=[a*i for i in range(1,10)]
        multiples_b=[b*i for i in range(1,10)]
        fig,ax=plt.subplots()
        ax.scatter(factors_a,[1]*len(factors_a), label="Factors A")
        ax.scatter(factors_b,[2]*len(factors_b), label="Factors B")
        ax.scatter(multiples_a,[3]*len(multiples_a), label="Multiples A")
        ax.scatter(multiples_b,[4]*len(multiples_b), label="Multiples B")
        ax.scatter(gcd,0.5,s=150, label="GCD")
        ax.scatter(lcm,2.5,s=150, label="LCM")
        ax.set_yticks([0.5,1,2,3,4,2.5])
        ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # Dynamic topics
    elif topic in dynamic_topics:
        file_path = f"topics/{topic.replace(' ','_')}.py"
        with open(file_path) as f:
            exec(f.read())

    # -------------------
    # Chat with teacher
    st.subheader("Chat with Teacher")
    learner_name = st.text_input("Your Name")
    teacher_number = st.text_input("Teacher Number")
    message = st.text_area("Message")
    if st.button("Send Message"):
        if learner_name and teacher_number and message:
            chat_file = f"messages/{teacher_number}.json"
            if os.path.exists(chat_file):
                with open(chat_file,"r") as f:
                    chats=json.load(f)
            else:
                chats=[]
            chats.append({"from": learner_name, "msg": message})
            with open(chat_file,"w") as f:
                json.dump(chats,f)
            st.success("Message sent!")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type=="Teacher":
    st.header("Teacher Portal")

    username=st.text_input("Username")
    password=st.text_input("Password",type="password")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered and logged in")
        elif teacher_data[username]==password:
            st.success("Login successful")
        else:
            st.error("Incorrect password")
        st.session_state.teacher_logged_in=True
        st.session_state.teacher_name=username

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic for Approval")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Topic"):
            submission = {"teacher": st.session_state.teacher_name,
                          "topic_name": topic_name,
                          "topic_description": topic_description}
            filename = topic_name.replace(" ","_")+".json"
            with open(f"submissions/{filename}","w") as f:
                json.dump(submission,f)
            st.success("Topic submitted for editor approval!")

        # Chat
        st.subheader("Chat with Learners")
        teacher_number = st.text_input("Your Teacher Number")
        chat_file = f"messages/{teacher_number}.json"
        if os.path.exists(chat_file):
            with open(chat_file,"r") as f:
                chats=json.load(f)
            for c in chats:
                st.write(f"{c['from']}: {c['msg']}")
        reply_name = st.text_input("Reply to (Learner Name)")
        reply_msg = st.text_area("Message")
        if st.button("Send Reply"):
            if reply_name and reply_msg:
                chats.append({"from": st.session_state.teacher_name, "msg": reply_msg})
                with open(chat_file,"w") as f:
                    json.dump(chats,f)
                st.success("Reply sent!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type=="Editor":
    st.header("Editor Dashboard")
    editor_pass = st.text_input("Editor Password", type="mercypaul")
    if st.button("Login Editor"):
        if editor_pass == "mercypaul":  # CHANGE THIS
            st.session_state.editor_logged_in=True
        else:
            st.error("Incorrect password")

    if st.session_state.editor_logged_in:
        st.subheader("Pending Submissions")
        repo_name = st.text_input("GitHub Repo (username/repo)")

        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.write(f"Teacher: {data['teacher']}")
            st.write(f"Topic: {data['topic_name']}")
            st.write(f"Description: {data['topic_description']}")
            if st.button(f"Generate Python Code for {data['topic_name']}", key=file):
                prompt = f"Write a Python program for the following math topic: {data['topic_description']}"
                try:
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        temperature=0,
                        max_tokens=500
                    )
                    generated_code = response.choices[0].text.strip()
                    st.code(generated_code)

                    if st.button(f"Approve & Push {data['topic_name']}", key=file+"_push"):
                        g = Github(GITHUB_TOKEN)
                        repo = g.get_repo(repo_name)
                        filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                        repo.create_file(filename, f"Add topic {data['topic_name']}", generated_code)
                        os.rename(file,f"approved/{os.path.basename(file)}")
                        st.success("Topic approved and pushed to GitHub!")

                except Exception as e:
                    st.error(f"OpenAI API Error: {e}")
