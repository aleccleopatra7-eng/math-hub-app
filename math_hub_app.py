import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from fractions import Fraction
from github import Github
import openai

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")
st.title("📊 Interactive Math Hub")

# -------------------------
# COLOR-BLIND MODE
# -------------------------
color_blind = st.toggle("🎨 Enable Color-Blind Mode")

if color_blind:
    COLORS = {
        "A": "black",
        "B": "gray",
        "C": "blue",
        "D": "purple"
    }
else:
    COLORS = {
        "A": "orange",
        "B": "blue",
        "C": "green",
        "D": "red"
    }

# -------------------------
# CREATE FOLDERS
# -------------------------
folders = ["submissions","approved","inbox","feedback"]
for folder in folders:
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
EDITOR_PASSWORD = "alex"

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner","Teacher","Editor"])

# =====================================================
# TOPICS
# =====================================================
topics = ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"]

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    topic = st.sidebar.selectbox("Choose Topic", topics)

    # -------------------------
    # LCM & GCD
    # -------------------------
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A",1,100,6)
        b = st.number_input("Number B",1,100,8)

        gcd = math.gcd(a,b)
        lcm = a*b//gcd

        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")

        factors_a = [i for i in range(1,a+1) if a%i==0]
        factors_b = [i for i in range(1,b+1) if b%i==0]

        fig,ax = plt.subplots()
        ax.scatter(factors_a,[1]*len(factors_a), color=COLORS["A"], label="Factors A")
        ax.scatter(factors_b,[2]*len(factors_b), color=COLORS["B"], label="Factors B")

        ax.scatter(lcm,2.5,color=COLORS["C"],s=120,label="LCM")
        ax.scatter(gcd,0.5,color=COLORS["D"],s=120,label="GCD")

        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # PRIME FACTORS TREE
    # -------------------------
    elif topic == "Prime Factors":
        st.subheader("Prime Factorization Tree")
        n = st.number_input("Enter number",2,100,12)

        temp=n
        i=2
        tree=[]
        while temp>1:
            if temp%i==0:
                tree.append((temp,i,temp//i))
                temp//=i
            else:
                i+=1

        for parent,factor,remainder in tree:
            st.write(f"{parent} → {factor} × {remainder}")

    # -------------------------
    # RATIOS
    # -------------------------
    elif topic == "Ratios":
        st.subheader("Simplified Ratios")
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)

        frac = Fraction(a,b)
        st.success(f"{a}:{b} → {frac.numerator}:{frac.denominator}")

    # -------------------------
    # SIMULTANEOUS EQUATIONS
    # -------------------------
    elif topic == "Simultaneous Equations":
        st.subheader("Simultaneous Equation Solver")

        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)

        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)

        if st.button("Solve"):
            det = a1*b2 - a2*b1

            if det !=0:
                x = (c1*b2 - c2*b1)/det
                y = (a1*c2 - a2*c1)/det

                st.success(f"x={x}, y={y}")

                x_vals = np.linspace(-10,10,400)
                y1_vals = (c1 - a1*x_vals)/b1
                y2_vals = (c2 - a2*x_vals)/b2

                fig,ax = plt.subplots()
                ax.plot(x_vals,y1_vals,color=COLORS["A"],label="Eq1")
                ax.plot(x_vals,y2_vals,color=COLORS["B"],label="Eq2")
                ax.scatter(x,y,color=COLORS["D"],s=120)

                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

            else:
                st.error("No solution")

    # -------------------------
    # INBOX
    # -------------------------
    st.subheader("📥 Send Request to Teacher")

    name = st.text_input("Your Name")
    code = st.text_input("Teacher Code")
    topic_req = st.text_input("Topic")
    msg = st.text_area("Message")

    if st.button("Send Request"):
        if name and code and msg:
            file = f"inbox/{code}.json"
            data = []
            if os.path.exists(file):
                with open(file,"r") as f:
                    data=json.load(f)

            data.append({"name":name,"topic":topic_req,"message":msg})

            with open(file,"w") as f:
                json.dump(data,f)

            st.success("Sent!")

    # -------------------------
    # FEEDBACK (GOES TO EDITOR)
    # -------------------------
    st.subheader("⭐ Rate This App")

    rating = st.slider("Rate (1-5)",1,5,3)
    comment = st.text_area("Comment")
    suggestion = st.text_area("Suggestion")

    if st.button("Submit Feedback"):
        file="feedback/feedback.json"
        data=[]
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)

        data.append({
            "role":"Learner",
            "rating":rating,
            "comment":comment,
            "suggestion":suggestion
        })

        with open(file,"w") as f:
            json.dump(data,f)

        st.success("Feedback sent to Editor!")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type=="Teacher":
    st.header("Teacher Section")

    user = st.text_input("Username")
    pwd = st.text_input("Password",type="password")
    code = st.text_input("Teacher Code")

    if st.button("Login/Register"):
        if user not in teacher_data:
            teacher_data[user]=pwd
            with open("teachers.json","w") as f:
                json.dump(teacher_data,f)
            st.success("Registered")
            st.session_state.teacher_logged_in=True
        elif teacher_data[user]==pwd:
            st.success("Logged in")
            st.session_state.teacher_logged_in=True
        else:
            st.error("Wrong password")

    if st.session_state.teacher_logged_in:

        st.subheader("📬 Student Requests")
        file=f"inbox/{code}.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
            for d in data:
                st.write(d["name"], "-", d["topic"])
                st.write(d["message"])
                st.write("------")

        # -------------------------
        # TEACHER SUGGESTIONS
        # -------------------------
        st.subheader("💡 Teacher Suggestions")

        suggestion = st.text_area("Give a suggestion to improve the system")

        if st.button("Submit Suggestion"):
            file="feedback/feedback.json"
            data=[]
            if os.path.exists(file):
                with open(file,"r") as f:
                    data=json.load(f)

            data.append({
                "role":"Teacher",
                "rating":None,
                "comment":"",
                "suggestion":suggestion
            })

            with open(file,"w") as f:
                json.dump(data,f)

            st.success("Suggestion sent to Editor!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type=="Editor":
    st.header("Editor Section")

    password = st.text_input("Enter Password", type="password")

    if password == EDITOR_PASSWORD:
        st.session_state.editor_logged_in = True

    if st.session_state.editor_logged_in:

        st.success("Access Granted")

        # -------------------------
        # VIEW ALL FEEDBACK
        # -------------------------
        st.subheader("⭐ All Feedback (Editor Only)")

        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)

            for d in data:
                st.write("Role:", d["role"])
                st.write("Rating:", d["rating"])
                st.write("Comment:", d["comment"])
                st.write("Suggestion:", d["suggestion"])
                st.write("------")
        else:
            st.info("No feedback yet")

        # -------------------------
        # SPECIAL GAME LOCK
        # -------------------------
        if not st.session_state.special_verified:
            st.subheader("🔐 Answer to Access Games")
            answer = st.text_input("who is my chizi?")

            if st.button("Submit Answer"):
                if answer.lower().strip() == "riya":
                    st.session_state.special_verified = True
                    st.success("Access granted 🎮")
                else:
                    st.error("Wrong answer")
        else:
            st.subheader("🎮 Mini Games")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
