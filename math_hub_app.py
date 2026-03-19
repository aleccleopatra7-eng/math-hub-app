import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import random
from fractions import Fraction
from github import Github
import openai

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")
st.title("📊 Interactive Math Hub")

# -------------------------
# CREATE FOLDERS
# -------------------------
for folder in ["submissions","approved","inbox","feedback"]:
    os.makedirs(folder, exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False
if "special_verified" not in st.session_state:
    st.session_state.special_verified = False
if "pre_questions" not in st.session_state:
    st.session_state.pre_questions = []
if "post_questions" not in st.session_state:
    st.session_state.post_questions = []
if "pre_score" not in st.session_state:
    st.session_state.pre_score = None
if "post_score" not in st.session_state:
    st.session_state.post_score = None

# -------------------------
# LOAD TEACHERS
# -------------------------
if os.path.exists("teachers.json"):
    with open("teachers.json","r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN","")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY","")
openai.api_key = OPENAI_API_KEY
EDITOR_PASSWORD = "aceluffy"

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner","Teacher","Editor"])

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def lcm(a,b):
    return abs(a*b)//math.gcd(a,b)

def generate_questions():
    qs=[]
    for _ in range(5):
        a=random.randint(2,12)
        b=random.randint(2,12)
        if random.choice(["LCM","GCD"])=="LCM":
            qs.append((f"LCM of {a} and {b}", lcm(a,b)))
        else:
            qs.append((f"GCD of {a} and {b}", math.gcd(a,b)))
    return qs

# =====================================================
# LEARNER
# =====================================================
if user_type=="Learner":
    st.header("Learner Section")

    topic = st.sidebar.selectbox("Choose Topic",
    ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations","Tests"])

    # ---------------- LCM & GCD ----------------
    if topic=="LCM & GCD":
        a=st.number_input("A",1,100,6)
        b=st.number_input("B",1,100,8)

        gcd=math.gcd(a,b)
        lcm_val=a*b//gcd

        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm_val}")

    # ---------------- PRIME ----------------
    elif topic=="Prime Factors":
        n=st.number_input("Number",2,100,12)
        temp=n
        i=2
        tree=[]
        while temp>1:
            if temp%i==0:
                tree.append((temp,i,temp//i))
                temp//=i
            else:
                i+=1

        st.markdown("### Factor Tree")
        for p,f,r in tree:
            st.write(f"{p} → {f} × {r}")

    # ---------------- RATIOS ----------------
    elif topic=="Ratios":
        a=st.number_input("A",1,100,4)
        b=st.number_input("B",1,100,6)
        frac=Fraction(a,b)
        st.success(f"Simplified: {frac.numerator}:{frac.denominator}")

    # ---------------- SIMULTANEOUS ----------------
    elif topic=="Simultaneous Equations":
        a1=st.number_input("a1",2)
        b1=st.number_input("b1",3)
        c1=st.number_input("c1",11)
        a2=st.number_input("a2",1)
        b2=st.number_input("b2",-1)
        c2=st.number_input("c2",1)

        if st.button("Solve"):
            det=a1*b2-a2*b1
            if det!=0:
                x=(c1*b2-c2*b1)/det
                y=(a1*c2-a2*c1)/det
                st.success(f"x={x}, y={y}")

    # ---------------- TEST SYSTEM ----------------
    elif topic=="Tests":
        tab1,tab2,tab3=st.tabs(["Pre-Test","Post-Test","Dashboard"])

        with tab1:
            if st.button("Generate Pre-Test"):
                st.session_state.pre_questions=generate_questions()

            for i,(q,_) in enumerate(st.session_state.pre_questions):
                st.session_state[f"pre_{i}"]=st.number_input(q,key=f"pre{i}")

            if st.button("Submit Pre"):
                score=0
                for i,(q,a) in enumerate(st.session_state.pre_questions):
                    if st.session_state[f"pre_{i}"]==a:
                        score+=6
                st.session_state.pre_score=score
                st.success(f"Score: {score}/30")

        with tab2:
            if st.button("Generate Post-Test"):
                st.session_state.post_questions=generate_questions()

            for i,(q,_) in enumerate(st.session_state.post_questions):
                st.session_state[f"post_{i}"]=st.number_input(q,key=f"post{i}")

            if st.button("Submit Post"):
                score=0
                for i,(q,a) in enumerate(st.session_state.post_questions):
                    if st.session_state[f"post_{i}"]==a:
                        score+=6
                st.session_state.post_score=score
                st.success(f"Score: {score}/30")

        with tab3:
            if st.session_state.pre_score and st.session_state.post_score:
                st.write("Improvement:", st.session_state.post_score - st.session_state.pre_score)

    # ---------------- INBOX ----------------
    st.subheader("📥 Send Request")
    name=st.text_input("Name")
    code=st.text_input("Teacher Code")
    msg=st.text_area("Message")

    if st.button("Send"):
        file=f"inbox/{code}.json"
        data=[]
        if os.path.exists(file):
            data=json.load(open(file))
        data.append({"name":name,"message":msg})
        json.dump(data,open(file,"w"))
        st.success("Sent!")

    # ---------------- FEEDBACK ----------------
    st.subheader("⭐ Rate App")
    rating=st.slider("Rating",1,5,3)
    comment=st.text_area("Comment")

    if st.button("Submit Feedback"):
        file="feedback/feedback.json"
        data=[]
        if os.path.exists(file):
            data=json.load(open(file))
        data.append({"rating":rating,"comment":comment})
        json.dump(data,open(file,"w"))
        st.success("Thanks!")

# =====================================================
# TEACHER
# =====================================================
elif user_type=="Teacher":
    st.header("Teacher")

    user=st.text_input("Username")
    pwd=st.text_input("Password",type="password")
    code=st.text_input("Code")

    if st.button("Login"):
        if user not in teacher_data:
            teacher_data[user]=pwd
            json.dump(teacher_data,open("teachers.json","w"))
        elif teacher_data[user]!=pwd:
            st.error("Wrong password")
        else:
            st.session_state.teacher_logged_in=True

    if st.session_state.teacher_logged_in:
        st.subheader("Requests")
        file=f"inbox/{code}.json"
        if os.path.exists(file):
            data=json.load(open(file))
            for d in data:
                st.write(d)

        st.subheader("Feedback")
        file="feedback/feedback.json"
        if os.path.exists(file):
            data=json.load(open(file))
            avg=sum(d["rating"] for d in data)/len(data)
            st.success(f"Average: {round(avg,2)} ⭐")

# =====================================================
# EDITOR
# =====================================================
elif user_type=="Editor":
    pwd=st.text_input("Password",type="password")
    if pwd==EDITOR_PASSWORD:
        st.session_state.editor_logged_in=True

    if st.session_state.editor_logged_in:
        st.success("Access Granted")

        if not st.session_state.special_verified:
            ans=st.text_input("who is my chizi?")
            if st.button("Submit"):
                if ans=="riya":
                    st.session_state.special_verified=True

        else:
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")

        st.subheader("Topic Management")
        repo_name=st.text_input("Repo")

        for file in os.listdir("submissions"):
            data=json.load(open(f"submissions/{file}"))
            st.write(data)

            if st.button(f"Generate {file}"):
                if OPENAI_API_KEY:
                    response=openai.Completion.create(
                        model="text-davinci-003",
                        prompt=data["topic_description"],
                        max_tokens=300
                    )
                    data["code"]=response.choices[0].text
                    json.dump(data,open(f"submissions/{file}","w"))
                    st.code(data["code"])
