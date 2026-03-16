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
# USER TYPE
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

    elif topic == "Prime Factors":
        st.subheader("Prime Factorization")
        num = st.number_input("Enter number", 2, 1000, 24)
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

    elif topic == "Ratios":
        st.subheader("Ratio Simplifier")
        a = st.number_input("First Number",1,100,4)
        b = st.number_input("Second Number",1,100,8)
        if st.button("Simplify Ratio"):
            g = math.gcd(a,b)
            st.success(f"Simplified Ratio: {a//g} : {b//g}")

    elif topic == "Simultaneous Equations":
        st.subheader("Solve Simple Simultaneous Equations")
        eq1 = st.text_input("Equation 1","2x + 3y = 11")
        eq2 = st.text_input("Equation 2","1x - 1y = 1")
        def parse_eq(eq):
            nums = list(map(int,re.findall(r'-?\d+',eq)))
            return nums[0],nums[1],nums[2]
        if st.button("Solve Equations"):
            try:
                a1,b1,c1 = parse_eq(eq1)
                a2,b2,c2 = parse_eq(eq2)
                det = a1*b2 - a2*b1
                if det!=0:
                    x = (c1*b2 - c2*b1)/det
                    y = (a1*c2 - a2*c1)/det
                    st.success(f"Solution: x={x}, y={y}")
                else:
                    st.error("No unique solution exists")
            except:
                st.error("Invalid format! Use ax + by = c")

    elif topic in dynamic_topics:
        file_path=f"topics/{topic.replace(' ','_')}.py"
        with open(file_path) as f:
            exec(f.read())

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
            st.success("Registered successfully")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
        elif teacher_data[username]==password:
            st.success("Login successful")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
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

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard")
    editor_pass_input = st.text_input("Enter Editor Password", type="password")
    editor_pass = st.secrets.get("EDITOR_PASSWORD","default_editor_pass")

    if editor_pass_input != editor_pass:
        st.error("Invalid password. Access denied.")
    else:
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
                if st.button(f"Approve {data['topic_name']}", key=file):
                    try:
                        g = Github(st.secrets["GITHUB_TOKEN"])
                        repo = g.get_repo(repo_name)
                        filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                        repo.create_file(filename,"Add topic",data["topic_code"])
                        os.rename(file,f"approved/{os.path.basename(file)}")
                        st.success("Topic approved and pushed to GitHub!")
                    except Exception as e:
                        st.error(e)
        else:
            st.info("No submissions yet")
