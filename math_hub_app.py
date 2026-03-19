import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from fractions import Fraction
from datetime import datetime
import random

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")

# -------------------------
# CREATE REQUIRED FOLDERS
# -------------------------
folders = ["submissions","approved","inbox","feedback","scores"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# -------------------------
# WELCOME PAGE
# -------------------------
st.markdown("<h1 style='text-align: center; color: orange;'>Welcome to My Math Interactive Hub! 🎉</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Explore, Learn, and Improve Your Math Skills!</p>", unsafe_allow_html=True)

# -------------------------
# SESSION STATE INIT
# -------------------------
session_keys = ["learner_name","teacher_code","learner_file",
                "pre_test_done","post_test_done","doing_pretest",
                "doing_posttest","doing_general_test","teacher_logged_in",
                "editor_logged_in","special_verified"]
for key in session_keys:
    if key not in st.session_state:
        st.session_state[key] = False if "done" not in key and "logged_in" not in key else False

# -------------------------
# SIDEBAR LOGIN
# -------------------------
st.sidebar.title("Login to Math Hub")
user_type = st.sidebar.radio("I am a:", ["Learner","Teacher","Editor"])
color_blind = st.sidebar.checkbox("🎨 Enable Color-Blind Mode")
COLORS = {"A": "black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

topics = ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"]

# -------------------------
# TEACHER DATA
# -------------------------
teachers_file = "teachers.json"
if os.path.exists(teachers_file):
    with open(teachers_file,"r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

EDITOR_PASSWORD = "alex"

# =========================
# LEARNER LOGIN
# =========================
if user_type=="Learner":
    learner_name = st.sidebar.text_input("Enter Your Name")
    teacher_code = st.sidebar.text_input("Enter Teacher Code")
    if st.sidebar.button("Login"):
        if learner_name and teacher_code:
            st.session_state.learner_name = learner_name.strip()
            st.session_state.teacher_code = teacher_code.strip()
            learner_file = f"scores/{st.session_state.learner_name}.json"
            st.session_state.learner_file = learner_file
            if os.path.exists(learner_file):
                with open(learner_file,"r") as f:
                    learner_data = json.load(f)
                st.session_state.pre_test_done = "pre_test" in learner_data
                st.session_state.post_test_done = "post_test" in learner_data
            else:
                learner_data = {}
                with open(learner_file,"w") as f:
                    json.dump(learner_data,f)
            st.success(f"Welcome, {st.session_state.learner_name}!")
        else:
            st.sidebar.error("Enter both name and teacher code.")

# =========================
# LEARNER SECTION
# =========================
if user_type=="Learner" and st.session_state.learner_name and st.session_state.teacher_code:
    st.sidebar.title("Activities")
    activity_options = ["Simulations"]
    if not st.session_state.pre_test_done or not st.session_state.post_test_done:
        activity_options.extend(["Pre-Test","Post-Test"])
    else:
        activity_options.append("General Test")
    activity = st.sidebar.radio("Choose Activity", activity_options)

    # -------------------------
    # PRE-TEST
    # -------------------------
    if activity=="Pre-Test":
        st.header("📝 Pre-Test (No Simulation Allowed)")
        st.info("Solve using your knowledge; simulations are disabled during this test.")
        pre_answers = {}
        st.subheader("LCM & GCD Questions")
        pre_answers["LCM"] = st.radio("LCM of 12 and 18?", [36, 54, 72, 24])
        pre_answers["GCD"] = st.radio("GCD of 24 and 36?", [12,6,18,24])
        st.subheader("Prime Factors")
        pre_answers["PrimeFactors"] = st.radio("Prime factors of 28?", ["2,2,7","2,7","2,2,2,7","7,4"])
        st.subheader("Ratios")
        pre_answers["Ratio"] = st.radio("Simplify ratio 12:18", ["2:3","3:4","2:2","4:6"])
        st.subheader("Simultaneous Equations")
        pre_answers["SimEq"] = st.radio("Solve x + y = 4, x - y = 2, find x?", [1,2,3,4])
        if st.button("Submit Pre-Test"):
            learner_data = {"pre_test": pre_answers,"post_test":{},"general_test":{},"simulations_completed":{},"teacher_code":st.session_state.teacher_code,"last_accessed":str(datetime.now())}
            with open(st.session_state.learner_file,"w") as f:
                json.dump(learner_data,f)
            st.success("Pre-Test submitted! You can now take the Post-Test.")
            st.session_state.pre_test_done = True

    # -------------------------
    # POST-TEST
    # -------------------------
    elif activity=="Post-Test":
        st.header("📝 Post-Test (Simulations Allowed)")
        st.info("Use simulations to help answer the questions.")
        post_answers = {}
        st.subheader("LCM & GCD Questions")
        a = st.number_input("Number A for LCM & GCD",1,100,6)
        b = st.number_input("Number B for LCM & GCD",1,100,8)
        post_answers["LCM"] = a*b//math.gcd(a,b)
        post_answers["GCD"] = math.gcd(a,b)

        st.subheader("Prime Factors")
        n = st.number_input("Number for Prime Factorization",2,100,12)
        temp=n
        i=2
        tree=[]
        while temp>1:
            if temp%i==0:
                tree.append((temp,i,temp//i))
                temp//=i
            else:
                i+=1
        post_answers["PrimeFactors"] = tree

        st.subheader("Ratios")
        val1 = st.number_input("Value A for Ratio",1,100,4)
        val2 = st.number_input("Value B for Ratio",1,100,6)
        frac = Fraction(val1,val2)
        post_answers["Ratio"] = f"{frac.numerator}:{frac.denominator}"

        st.subheader("Simultaneous Equations")
        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)

        if st.button("Submit Post-Test"):
            if os.path.exists(st.session_state.learner_file):
                with open(st.session_state.learner_file,"r") as f:
                    learner_data = json.load(f)
            learner_data["post_test"] = post_answers
            learner_data["last_accessed"] = str(datetime.now())
            with open(st.session_state.learner_file,"w") as f:
                json.dump(learner_data,f)
            st.success("Post-Test submitted! Simulations are now fully available.")
            st.session_state.post_test_done = True

            # Improvement Graph
            st.subheader("📈 Improvement Graph")
            fig,ax = plt.subplots()
            pre_vals = [int(learner_data["pre_test"].get("LCM",0)),
                        int(learner_data["pre_test"].get("GCD",0)),
                        0,0]
            post_vals = [post_answers["LCM"],post_answers["GCD"],0,0]
            labels = ["LCM","GCD","Ratio","SimEq"]
            ax.bar(np.arange(len(labels))-0.15, pre_vals, width=0.3, label="Pre-Test", color="red")
            ax.bar(np.arange(len(labels))+0.15, post_vals, width=0.3, label="Post-Test", color="green")
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels)
            ax.set_ylabel("Scores / Values")
            ax.legend()
            st.pyplot(fig)

    # -------------------------
    # GENERAL TEST
    # -------------------------
    elif activity=="General Test":
        st.header("📝 General Test (Simulations Allowed)")
        st.info("Random questions across all topics; simulations are available.")
        general_answers = {}
        # LCM & GCD random question
        a = random.randint(2,20)
        b = random.randint(2,20)
        general_answers["LCM"] = a*b//math.gcd(a,b)
        general_answers["GCD"] = math.gcd(a,b)
        st.write(f"Find LCM and GCD of {a} and {b}")
        lcm_input = st.number_input("LCM Answer",value=0)
        gcd_input = st.number_input("GCD Answer",value=0)
        # Prime factor random question
        pf_num = random.randint(10,50)
        st.write(f"Prime factors of {pf_num}?")
        pf_input = st.text_input("Enter as comma separated numbers","")
        # Ratios
        r1,r2 = random.randint(2,20), random.randint(2,20)
        st.write(f"Simplify the ratio {r1}:{r2}")
        ratio_input = st.text_input("Enter ratio as x:y","")
        # Simultaneous equation
        sa1,sb1,sc1 = random.randint(1,5),random.randint(1,5),random.randint(5,15)
        sa2,sb2,sc2 = random.randint(1,5),random.randint(1,5),random.randint(5,15)
        st.write(f"Solve equations: {sa1}x + {sb1}y = {sc1}, {sa2}x + {sb2}y = {sc2}")
        se_x = st.number_input("x value",0)
        se_y = st.number_input("y value",0)

        if st.button("Submit General Test"):
            general_answers["LCM_user"]=lcm_input
            general_answers["GCD_user"]=gcd_input
            general_answers["PrimeFactors_user"]=pf_input
            general_answers["Ratio_user"]=ratio_input
            general_answers["SimEq_user"]={"x":se_x,"y":se_y}
            if os.path.exists(st.session_state.learner_file):
                with open(st.session_state.learner_file,"r") as f:
                    learner_data = json.load(f)
            learner_data["general_test"] = general_answers
            learner_data["last_accessed"]=str(datetime.now())
            with open(st.session_state.learner_file,"w") as f:
                json.dump(learner_data,f)
            st.success("General Test submitted!")

    # -------------------------
    # SIMULATIONS
    # -------------------------
    elif activity=="Simulations":
        st.header("🔬 Interactive Simulations")
        sim_topic = st.selectbox("Choose Simulation", topics)
        # LCM & GCD
        if sim_topic=="LCM & GCD":
            st.subheader("LCM & GCD Visualizer")
            a = st.number_input("Number A",1,100,6,key="sim_a")
            b = st.number_input("Number B",1,100,8,key="sim_b")
            gcd = math.gcd(a,b)
            lcm = a*b//gcd
            st.success(f"GCD = {gcd}, LCM = {lcm}")
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

        # Prime Factors
        elif sim_topic=="Prime Factors":
            st.subheader("Prime Factorization Tree")
            n = st.number_input("Enter number",2,100,12,key="pf")
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

        # Ratios
        elif sim_topic=="Ratios":
            st.subheader("Simplified Ratios")
            a = st.number_input("Value A",1,100,4,key="r_a")
            b = st.number_input("Value B",1,100,6,key="r_b")
            frac = Fraction(a,b)
            st.success(f"{a}:{b} → {frac.numerator}:{frac.denominator}")

        # Simultaneous Equations
        elif sim_topic=="Simultaneous Equations":
            st.subheader("Simultaneous Equation Solver")
            a1 = st.number_input("a1", value=2,key="sx1")
            b1 = st.number_input("b1", value=3,key="sy1")
            c1 = st.number_input("c1", value=11,key="sc1")
            a2 = st.number_input("a2", value=1,key="sx2")
            b2 = st.number_input("b2", value=-1,key="sy2")
            c2 = st.number_input("c2", value=1,key="sc2")
            if st.button("Solve Equations"):
                det = a1*b2 - a2*b1
                if det!=0:
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
                    st.error("No solution exists")

# =========================
# TEACHER SECTION
# =========================
elif user_type=="Teacher":
    st.header("Teacher Section")
    user = st.text_input("Username")
    pwd = st.text_input("Password",type="password")
    code = st.text_input("Teacher Code")
    if st.button("Login/Register"):
        if user not in teacher_data:
            teacher_data[user]=pwd
            with open(teachers_file,"w") as f:
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

# =========================
# EDITOR SECTION
# =========================
elif user_type=="Editor":
    st.header("Editor Section")
    password = st.text_input("Enter Password", type="password")
    if password == EDITOR_PASSWORD:
        st.session_state.editor_logged_in = True
    if st.session_state.editor_logged_in:
        st.success("Access Granted")
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
        # Special Game Lock
        if not st.session_state.special_verified:
            st.subheader("🔐 Answer to Access Games")
            answer = st.text_input("Who is my chizi?")
            if st.button("Submit Answer"):
                if answer.lower().strip() == "riya":
                    st.session_state.special_verified = True
                    st.success("Access granted 🎮")
                else:
                    st.error("Wrong answer")
        else:
            st.subheader("🎮 Mini Games")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
