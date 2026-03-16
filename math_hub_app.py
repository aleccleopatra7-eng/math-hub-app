import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re
import json
from email.message import EmailMessage
import smtplib
from github import Github
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

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "learner_name" not in st.session_state:
    st.session_state.learner_name = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

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
# CHAT FILE
# -------------------------
CHAT_FILE = "chat.json"
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        st.session_state.chat_messages = json.load(f)
else:
    st.session_state.chat_messages = []

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    learner_name = st.text_input("Enter your name", key="learner_input")
    if learner_name:
        st.session_state.learner_name = learner_name

        # Topics
        default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
        dynamic_topics = []
        for file in glob.glob("topics/*.py"):
            name = os.path.basename(file).replace(".py", "").replace("_"," ")
            dynamic_topics.append(name)
        topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

        # -------------------------
        # LCM & GCD
        # -------------------------
        if topic == "LCM & GCD":
            st.subheader("LCM & GCD Visualizer")
            a = st.number_input("Number A", 1, 100, 6)
            b = st.number_input("Number B", 1, 100, 8)
            gcd = math.gcd(a,b)
            lcm = a*b//gcd
            st.success(f"GCD = {gcd} | LCM = {lcm}")

            factors_a=[i for i in range(1,a+1) if a%i==0]
            factors_b=[i for i in range(1,b+1) if b%i==0]
            multiples_a=[a*i for i in range(1,10)]
            multiples_b=[b*i for i in range(1,10)]

            fig,ax=plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a), color="orange", label="Factors A")
            ax.scatter(factors_b,[2]*len(factors_b), color="blue", label="Factors B")
            ax.scatter(multiples_a,[3]*len(multiples_a), color="green", label="Multiples A")
            ax.scatter(multiples_b,[4]*len(multiples_b), color="red", label="Multiples B")
            ax.scatter(gcd,0.5,s=150, color="black", label="GCD")
            ax.scatter(lcm,2.5,s=150, color="purple", label="LCM")
            for x in factors_a: ax.text(x,1.05,str(x),ha="center")
            for x in factors_b: ax.text(x,2.05,str(x),ha="center")
            for x in multiples_a: ax.text(x,3.05,str(x),ha="center")
            for x in multiples_b: ax.text(x,4.05,str(x),ha="center")
            ax.set_yticks([0.5,1,2,3,4,2.5])
            ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        # -------------------------
        # PRIME FACTORS
        # -------------------------
        elif topic == "Prime Factors":
            st.subheader("Prime Factorization")
            num = st.number_input("Enter a number", 2)
            def prime_factors(n):
                factors=[]
                d=2
                while n>1:
                    while n%d==0:
                        factors.append(d)
                        n//=d
                    d+=1
                return factors
            if st.button("Find Prime Factors"):
                factors = prime_factors(num)
                st.success(f"Prime Factors: {factors}")

        # -------------------------
        # RATIOS
        # -------------------------
        elif topic == "Ratios":
            st.subheader("Simplify Ratio")
            a = st.number_input("First number", 1)
            b = st.number_input("Second number", 1)
            if st.button("Simplify Ratio"):
                g = math.gcd(a,b)
                st.success(f"Simplified Ratio: {a//g} : {b//g}")

        # -------------------------
        # SIMULTANEOUS EQUATIONS
        # -------------------------
        elif topic == "Simultaneous Equations":
            st.subheader("Simultaneous Equation Solver")
            eq1 = st.text_input("Equation 1 (ax + by = c)")
            eq2 = st.text_input("Equation 2 (ax + by = c)")
            def parse_eq(eq):
                nums = list(map(int,re.findall(r'-?\d+',eq)))
                return nums[0], nums[1], nums[2]
            if st.button("Solve Equations"):
                try:
                    a1,b1,c1 = parse_eq(eq1)
                    a2,b2,c2 = parse_eq(eq2)
                    det = a1*b2 - a2*b1
                    if det!=0:
                        x=(c1*b2 - c2*b1)/det
                        y=(a1*c2 - a2*c1)/det
                        st.success(f"x={x}, y={y}")
                        x_vals = np.linspace(-10,10,400)
                        y1=(c1 - a1*x_vals)/b1
                        y2=(c2 - a2*x_vals)/b2
                        fig,ax=plt.subplots()
                        ax.plot(x_vals,y1,label="Eq1")
                        ax.plot(x_vals,y2,label="Eq2")
                        ax.scatter(x,y,color="red",s=100,label="Solution")
                        ax.legend()
                        st.pyplot(fig)
                    else:
                        st.error("No unique solution exists!")
                except:
                    st.error("Invalid format!")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username]=password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered & logged in!")
        elif teacher_data[username]==password:
            st.success("Login successful!")
        else:
            st.error("Incorrect password!")

        st.session_state.teacher_logged_in = True
        st.session_state.teacher_name=username

    if st.session_state.teacher_logged_in:
        st.subheader("Submit a Topic")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Description")
        topic_code = st.text_area("Python Code")
        if st.button("Submit Topic for Approval"):
            submission = {
                "teacher": st.session_state.teacher_name,
                "topic_name": topic_name,
                "topic_description": topic_description,
                "topic_code": topic_code
            }
            filename = topic_name.replace(" ","_")+".json"
            with open(f"submissions/{filename}","w") as f:
                json.dump(submission,f)
            st.success("Topic submitted! Editor will review.")

        # -------------------------
        # TEACHER-LEARNER CHAT
        # -------------------------
        st.subheader("Chat with Learners")
        message = st.text_input("Type a message")
        if st.button("Send Message"):
            chat_entry = {
                "sender": st.session_state.teacher_name,
                "message": message,
                "time": str(datetime.now())
            }
            st.session_state.chat_messages.append(chat_entry)
            with open(CHAT_FILE,"w") as f:
                json.dump(st.session_state.chat_messages,f)
        st.write("**Chat History**")
        for c in st.session_state.chat_messages:
            st.write(f"{c['sender']} ({c['time']}): {c['message']}")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard")
    editor_password = st.text_input("Enter Editor Password", type="password")
    if editor_password != "YOUR_EDITOR_PASSWORD":
        st.warning("Enter correct password to access submissions.")
    else:
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")
        if submissions:
            for file in submissions:
                with open(file) as f:
                    data=json.load(f)
                st.subheader(data["topic_name"])
                st.info(f"Teacher: {data['teacher']}")
                st.write(data["topic_description"])
                st.code(data["topic_code"])
                notes = st.text_area(f"Notes for {data['topic_name']}", key=file+"_notes")
                if st.button(f"Approve & Push {data['topic_name']}", key=file+"_approve"):
                    try:
                        g = Github(st.secrets["GITHUB_TOKEN"])
                        repo = g.get_repo(repo_name)
                        filename=f"topics/{data['topic_name'].replace(' ','_')}.py"
                        try:
                            existing_file = repo.get_contents(filename)
                            repo.update_file(existing_file.path,f"Update {data['topic_name']}",data["topic_code"],existing_file.sha)
                        except:
                            repo.create_file(filename,f"Add {data['topic_name']}",data["topic_code"])
                        os.rename(file,f"approved/{os.path.basename(file)}")
                        st.success("Topic approved and pushed to GitHub!")
                    except Exception as e:
                        st.error(e)
        else:
            st.info("No submissions yet")
