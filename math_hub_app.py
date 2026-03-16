import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
import re
from email.message import EmailMessage
import smtplib
from github import Github
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

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""

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
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =========================
# LEARNER SECTION
# =========================
if user_type == "Learner":

    st.header("Learner Section")
    st.write("Choose a topic from the sidebar to explore.")

    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]

    dynamic_topics = []
    for file in glob.glob("topics/*.py"):
        name = os.path.basename(file).replace(".py", "").replace("_"," ")
        dynamic_topics.append(name)

    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    # -------------------------
    # BUILT-IN LCM & GCD
    # -------------------------
    if topic == "LCM & GCD":

        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)

        gcd = math.gcd(a,b)
        lcm = a*b//gcd

        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")

        # Factors & multiples
        factors_a=[i for i in range(1,a+1) if a%i==0]
        factors_b=[i for i in range(1,b+1) if b%i==0]
        multiples_a=[a*i for i in range(1,10)]
        multiples_b=[b*i for i in range(1,10)]

        colorblind = st.checkbox("Enable color-blind friendly mode")

        fig,ax=plt.subplots()
        y_positions = [1,2,3,4]

        ax.scatter(factors_a,[y_positions[0]]*len(factors_a), marker="s", color="orange" if not colorblind else "black", label="Factors A")
        ax.scatter(factors_b,[y_positions[1]]*len(factors_b), marker="s", color="blue" if not colorblind else "gray", label="Factors B")
        ax.scatter(multiples_a,[y_positions[2]]*len(multiples_a), marker="o", color="green" if not colorblind else "purple", label="Multiples A")
        ax.scatter(multiples_b,[y_positions[3]]*len(multiples_b), marker="o", color="red" if not colorblind else "brown", label="Multiples B")
        ax.scatter(lcm,2.5, color="green" if not colorblind else "purple", s=120, label="LCM")
        ax.scatter(gcd,0.5, color="orange" if not colorblind else "black", s=120, label="GCD")

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
        # STEP-BY-STEP FACTORIZATION
        # -------------------------
        st.subheader("Step-by-Step Factorization")
        st.write("Factors of each number:")
        for i in range(1,a+1):
            if a % i == 0:
                st.write(f"{i} is a factor of {a}")
        for i in range(1,b+1):
            if b % i == 0:
                st.write(f"{i} is a factor of {b}")
        common_factors = [i for i in range(1,min(a,b)+1) if a%i==0 and b%i==0]
        st.write(f"Common factors: {common_factors}")
        st.write(f"✅ GCD = {gcd}")

        # -------------------------
        # MULTIPLES SIMULATION FOR LCM
        # -------------------------
        st.subheader("Multiples Simulation for LCM")
        mult_a = a
        mult_b = b
        step = 1
        while mult_a != mult_b:
            st.write(f"Step {step}: {a} multiples → {mult_a}, {b} multiples → {mult_b}")
            if mult_a < mult_b:
                mult_a += a
            else:
                mult_b += b
            step += 1
            time.sleep(0.5)
        st.write(f"✅ LCM = {mult_a}")

    # -------------------------
    # DYNAMIC TOPICS
    # -------------------------
    elif topic in dynamic_topics:
        file_path=f"topics/{topic.replace(' ','_')}.py"
        with open(file_path) as f:
            exec(f.read())

# =========================
# TEACHER SECTION
# =========================
elif user_type == "Teacher":

    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register / Login"):

        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
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

        st.subheader("Submit Topic")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Description")
        topic_code = st.text_area("Python Code")

        if st.button("Submit Topic"):

            submission = {
                "teacher": st.session_state.teacher_name,
                "topic_name": topic_name,
                "topic_description": topic_description,
                "topic_code": topic_code
            }

            filename = topic_name.replace(" ","_")+".json"
            with open(f"submissions/{filename}","w") as f:
                json.dump(submission,f)

            st.success("Topic submitted for approval!")

            # -------------------------
            # EMAIL NOTIFICATION TO EDITOR
            # -------------------------
            email_sender = "aleccleopatra7@gmail.com"
            email_password = "aceluffy#"
            recipients = ["aleccleopatra7@gmail.com","alecriya22@gmail.com"]

            msg = EmailMessage()
            msg['Subject'] = f"New Topic Submitted: {topic_name}"
            msg['From'] = email_sender
            msg['To'] = ", ".join(recipients)
            msg.set_content(f"Topic: {topic_name}\nDescription:\n{topic_description}\nCode:\n{topic_code}")

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.send_message(msg)
                st.success("Editor notified via email!")
            except Exception as e:
                st.error(f"Failed to send email: {e}")

# =========================
# EDITOR SECTION
# =========================
elif user_type == "Editor":

    st.header("Editor Dashboard")
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

            if st.button(f"Approve {data['topic_name']}", key=file):
                try:
                    g = Github(st.secrets["GITHUB_TOKEN"])
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    repo.create_file(filename, "Add topic", data["topic_code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)
    else:
        st.info("No submissions yet")
