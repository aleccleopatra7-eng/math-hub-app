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

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊", layout="centered")
st.title("📊 Interactive Math Hub")

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# -------------------------
# PASSWORD FILE (for teachers)
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# LEARNER SECTION
# -------------------------
if user_type == "Learner":
    st.header("Learner Section")
    st.write("Choose a topic from the sidebar to explore.")

    # Built-in topics
    default_topics = {
        "LCM & GCD": "built-in",
        "Prime Factors": "built-in",
        "Ratios": "built-in",
        "Simultaneous Equations": "built-in"
    }

    # Load dynamic topics
    dynamic_topics = {}
    if os.path.exists("topics"):
        for f in glob.glob("topics/*.py"):
            name = os.path.basename(f).replace("_", " ").replace(".py", "")
            dynamic_topics[name] = f

    all_topics = list(default_topics.keys()) + list(dynamic_topics.keys())
    tool = st.sidebar.selectbox("Choose Topic", all_topics)

    if tool in dynamic_topics:
        st.subheader(f"Dynamic Topic: {tool}")
        with open(dynamic_topics[tool], "r") as f:
            exec(f.read())
    else:
        # BUILT-IN TOPICS
        if tool == "LCM & GCD":
            st.header("LCM & GCD Visualizer")
            a = st.number_input("Number 1", 1, 50, 6)
            b = st.number_input("Number 2", 1, 50, 8)
            gcd = math.gcd(a, b)
            lcm = a * b // gcd
            st.success(f"GCD = {gcd}")
            st.success(f"LCM = {lcm}")

            st.subheader("Factors & Multiples")
            factors_a = [i for i in range(1, a+1) if a % i == 0]
            factors_b = [i for i in range(1, b+1) if b % i == 0]
            multiples_a = [a*i for i in range(1, 10)]
            multiples_b = [b*i for i in range(1, 10)]
            colorblind = st.checkbox("Enable color-blind friendly mode")

            fig, ax = plt.subplots()
            y_positions = [1,2,3,4]
            ax.scatter(factors_a, [y_positions[0]]*len(factors_a),
                       marker="s", color="orange" if not colorblind else "black", label="Factors A")
            ax.scatter(factors_b, [y_positions[1]]*len(factors_b),
                       marker="s", color="blue" if not colorblind else "gray", label="Factors B")
            ax.scatter(multiples_a, [y_positions[2]]*len(multiples_a),
                       marker="o", color="green" if not colorblind else "purple", label="Multiples A")
            ax.scatter(multiples_b, [y_positions[3]]*len(multiples_b),
                       marker="o", color="red" if not colorblind else "brown", label="Multiples B")
            ax.scatter(lcm, 2.5, color="green" if not colorblind else "purple", s=120, label="LCM")
            ax.scatter(gcd, 0.5, color="orange" if not colorblind else "black", s=120, label="GCD")

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
# TEACHER SECTION
# -------------------------
elif user_type == "Teacher":
    st.header("Teacher Section")
    st.write("Login to submit new math topics. Editor approval required.")

    teacher_name = st.text_input("Teacher Username")
    teacher_password = st.text_input("Password", type="password")

    # Teacher registration if new
    if st.button("Register / Login"):
        if teacher_name not in teacher_data:
            teacher_data[teacher_name] = teacher_password
            with open(PASSWORD_FILE, "w") as f:
                json.dump(teacher_data, f)
            st.success("Registered successfully! Logged in.")
        elif teacher_data.get(teacher_name) == teacher_password:
            st.success("Login successful!")
        else:
            st.error("Incorrect password.")

        # Topic submission form
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        topic_code = st.text_area("Topic Code")

        if st.button("Submit Topic for Approval"):
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
                st.success("Topic submitted! Editor notified via email.")
            except Exception as e:
                st.error(f"Failed to send email: {e}")

# -------------------------
# EDITOR SECTION
# -------------------------
elif user_type == "Editor":
    st.header("Editor Dashboard")
    st.write("Approve new topics submitted by teachers and push to GitHub.")

    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = st.text_input("GitHub repo (username/repo)")

    topic_file = st.file_uploader("Upload teacher submitted topic (.py)")
    if st.button("Approve & Push"):
        if topic_file and github_token:
            try:
                content = topic_file.read().decode("utf-8")
                g = Github(github_token)
                repo = g.get_repo(repo_name)
                file_name = f"topics/{topic_file.name}"
                try:
                    existing_file = repo.get_contents(file_name)
                    repo.update_file(existing_file.path, f"Update topic {topic_file.name}", content, existing_file.sha)
                    st.success("Topic updated in GitHub repo!")
                except:
                    repo.create_file(file_name, f"Add topic {topic_file.name}", content)
                    st.success("Topic added to GitHub repo!")
            except Exception as e:
                st.error(f"Error pushing to GitHub: {e}")
        else:
            st.error("Upload a file and ensure GITHUB_TOKEN is set.")
