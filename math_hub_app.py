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
folders = ["scores","feedback","inbox"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# -------------------------
# ANIMATED WELCOME
# -------------------------
st.markdown("""
<h1 style='text-align:center; color:orange; animation: fadeIn 2s;'>
🎉 Welcome to My Math Interactive Hub
</h1>
<style>
@keyframes fadeIn {
    from {opacity: 0; transform: scale(0.5);}
    to {opacity: 1; transform: scale(1);}
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
for key in ["learner_name","teacher_logged","editor_logged","special_verified"]:
    if key not in st.session_state:
        st.session_state[key] = False

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Login")
user_type = st.sidebar.radio("I am:", ["Learner","Teacher","Editor"])
color_blind = st.sidebar.checkbox("🎨 Color-Blind Mode")
COLORS = {"A":"black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

# -------------------------
# LEARNER LOGIN
# -------------------------
if user_type=="Learner":
    name = st.sidebar.text_input("Name")
    teacher_code = st.sidebar.text_input("Teacher Code")

    if st.sidebar.button("Login"):
        if name and teacher_code:
            st.session_state.learner_name = name.strip()
            st.session_state.teacher_code = teacher_code.strip()
            st.success(f"Welcome {name}!")

# -------------------------
# LEARNER SECTION
# -------------------------
if user_type=="Learner" and st.session_state.learner_name:

    file = f"scores/{st.session_state.learner_name}.json"
    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
    else:
        data = {"history":[]}
        with open(file,"w") as f:
            json.dump(data,f)

    pre_done = "pre_score" in data
    post_done = "post_score" in data

    options = ["Simulations"]
    if not pre_done or not post_done:
        options += ["Pre-Test","Post-Test"]
    else:
        options += ["General Test"]

    activity = st.sidebar.radio("Activities", options)

    # -------------------------
    # PRE TEST
    # -------------------------
    if activity=="Pre-Test":
        st.header("📝 Pre-Test (No Simulations Allowed)")
        st.info("Solve the questions using your knowledge.")

        ans = {}
        ans["LCM"] = st.radio("LCM of 24, 36 and 60?", [360,720,180,240])
        ans["GCD"] = st.radio("GCD of 48 and 72?", [12,24,36,6])
        ans["Ratio"] = st.radio("Simplify 45:60", ["3:4","4:5","5:6"])
        ans["SimEq"] = st.radio("x+y=10, x-y=2 → x=?", [4,5,6])

        if st.button("Submit Pre-Test"):
            score = 0
            if ans["LCM"]==360: score+=1
            if ans["GCD"]==24: score+=1
            if ans["Ratio"]=="3:4": score+=1
            if ans["SimEq"]==6: score+=1

            data["pre_score"]=score
            with open(file,"w") as f:
                json.dump(data,f)

            st.success(f"Score: {score}/4")

    # -------------------------
    # POST TEST
    # -------------------------
    elif activity=="Post-Test":
        st.header("📝 Post-Test (Simulations Allowed)")

        a = st.number_input("Number A for LCM & GCD",10,50,12)
        b = st.number_input("Number B for LCM & GCD",10,50,18)

        if st.button("Submit Post-Test"):
            # LCM & GCD
            correct_lcm = a*b//math.gcd(a,b)
            correct_gcd = math.gcd(a,b)
            score = 2

            data["post_score"]=score
            pre = data.get("pre_score",0)
            improvement = score - pre
            percent = (improvement/4)*100

            data["history"].append({"date":str(datetime.now()),"pre":pre,"post":score})
            with open(file,"w") as f:
                json.dump(data,f)

            st.subheader("📊 Results")
            st.write(f"Pre-Test Score: {pre}/4")
            st.write(f"Post-Test Score: {score}/4")
            st.success(f"Improvement: {improvement}")
            st.success(f"{percent:.1f}% Improvement")

            # LCM & GCD Visual
            st.subheader("📈 LCM & GCD Visualizer")
            fig,ax = plt.subplots()
            factors_a = [i for i in range(1,a+1) if a%i==0]
            factors_b = [i for i in range(1,b+1) if b%i==0]
            ax.scatter(factors_a,[1]*len(factors_a), color=COLORS["A"], label=f"Factors of {a}")
            ax.scatter(factors_b,[2]*len(factors_b), color=COLORS["B"], label=f"Factors of {b}")
            ax.scatter([correct_lcm],[1.5],color=COLORS["C"],s=100,label="LCM")
            ax.scatter([correct_gcd],[2.5],color=COLORS["D"],s=100,label="GCD")
            ax.set_yticks([1,1.5,2,2.5])
            ax.set_yticklabels([f"{a} factors","LCM","{b} factors","GCD"])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

    # -------------------------
    # GENERAL TEST
    # -------------------------
    elif activity=="General Test":
        st.header("📝 General Test")
        a,b = random.randint(5,30),random.randint(5,30)
        st.write(f"LCM of {a} and {b}?")
        ans = st.number_input("Answer")
        if st.button("Submit"):
            correct = a*b//math.gcd(a,b)
            score = 1 if ans==correct else 0
            data["general_score"]=score
            with open(file,"w") as f:
                json.dump(data,f)
            st.success(f"Score: {score}/1")

    # -------------------------
    # SIMULATIONS
    # -------------------------
    elif activity=="Simulations":
        topic = st.selectbox("Choose Topic", ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"])

        # LCM & GCD
        if topic=="LCM & GCD":
            a = st.number_input("A",2,50)
            b = st.number_input("B",2,50)
            st.write("Factors A:", [i for i in range(1,a+1) if a%i==0])
            st.write("Factors B:", [i for i in range(1,b+1) if b%i==0])
            st.write("Multiples A:", [a*i for i in range(1,6)])
            st.write("Multiples B:", [b*i for i in range(1,6)])
            gcd = math.gcd(a,b)
            lcm = a*b//gcd
            st.success(f"GCD={gcd}, LCM={lcm}")
            # Visualizer
            fig,ax = plt.subplots()
            ax.scatter([i for i in range(1,a+1) if a%i==0],[1]*len([i for i in range(1,a+1) if a%i==0]),color=COLORS["A"],label=f"Factors {a}")
            ax.scatter([i for i in range(1,b+1) if b%i==0],[2]*len([i for i in range(1,b+1) if b%i==0]),color=COLORS["B"],label=f"Factors {b}")
            ax.scatter([lcm],[1.5],color=COLORS["C"],s=100,label="LCM")
            ax.scatter([gcd],[2.5],color=COLORS["D"],s=100,label="GCD")
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        # Prime Factors
        elif topic=="Prime Factors":
            n = st.number_input("Number",2,100)
            temp = n
            i=2
            while temp>1:
                if temp%i==0:
                    st.write(f"{temp} → {i} × {temp//i}")
                    temp//=i
                else:
                    i+=1

        # Ratios
        elif topic=="Ratios":
            a = st.number_input("A",1,50)
            b = st.number_input("B",1,50)
            frac = Fraction(a,b)
            st.success(f"{frac.numerator}:{frac.denominator}")

        # Simultaneous Equations
        elif topic=="Simultaneous Equations":
            st.subheader("Enter Equations: a1x + b1y = c1, a2x + b2y = c2")
            a1 = st.number_input("a1",2)
            b1 = st.number_input("b1",3)
            c1 = st.number_input("c1",11)
            a2 = st.number_input("a2",1)
            b2 = st.number_input("b2",-1)
            c2 = st.number_input("c2",1)

            st.write("Equations entered:")
            st.latex(f"{a1}x + {b1}y = {c1}")
            st.latex(f"{a2}x + {b2}y = {c2}")

            method = st.selectbox("Method", ["Elimination","Substitution"])
            if st.button("Solve Step-by-Step"):
                det = a1*b2 - a2*b1
                if det==0:
                    st.error("No solution exists")
                else:
                    # Substitution
                    if method=="Substitution":
                        st.write("Step 1: Make x subject from 2nd eq")
                        st.latex(f"x = ({c2} - {b2}y)/{a2}")
                        x = (c1*b2 - c2*b1)/det
                        y = (a1*c2 - a2*c1)/det
                        st.write(f"x = {x}, y = {y}")
                    else:
                        # Elimination
                        m = a1
                        st.write("Step 1: Multiply equation 2 by a1")
                        st.latex(f"{m*a2}x + {m*b2}y = {m*c2}")
                        st.write("Step 2: Subtract eq2 from eq1")
                        y = (c1*m - m*c2)/(b1*m - m*b2)
                        x = (c1 - b1*y)/a1
                        st.write(f"x = {x}, y = {y}")

                    # Graph
                    x_vals = np.linspace(-10,10,400)
                    y1_vals = (c1 - a1*x_vals)/b1
                    y2_vals = (c2 - a2*x_vals)/b2
                    fig,ax = plt.subplots()
                    ax.plot(x_vals,y1_vals,color=COLORS["A"],label="Eq1")
                    ax.plot(x_vals,y2_vals,color=COLORS["B"],label="Eq2")
                    ax.scatter(x,y,color=COLORS["D"],s=120,label="Intersection")
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)

# -------------------------
# TEACHER SECTION
# -------------------------
elif user_type=="Teacher":
    st.header("Teacher Section")
    code = st.text_input("Teacher Code")

    st.subheader("📬 Student Requests")
    file = f"inbox/{code}.json"
    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
        for d in data:
            st.write(d)
    else:
        st.info("No requests")

    st.subheader("💡 Send Suggestion")
    suggestion = st.text_area("Suggestion")
    if st.button("Submit Suggestion"):
        file="feedback/feedback.json"
        data=[]
        if os.path.exists(file):
            with open(file) as f:
                data=json.load(f)
        data.append({"role":"Teacher","suggestion":suggestion})
        with open(file,"w") as f:
            json.dump(data,f)
        st.success("Sent to editor")

# -------------------------
# EDITOR SECTION
# -------------------------
elif user_type=="Editor":
    st.header("Editor Section")
    password = st.text_input("Password", type="password")
    if password=="alex":
        st.success("Access Granted")
        st.subheader("📊 Feedback")
        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file) as f:
                data=json.load(f)
            for d in data:
                st.write(d)

        st.subheader("🔐 Secret Access")
        answer = st.text_input("Who is my chizi?")
        if answer.lower()=="riya":
            st.success("Unlocked 🎮")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
