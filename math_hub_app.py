import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from fractions import Fraction
from datetime import datetime
import random
import uuid

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")

# -------------------------
# CREATE FOLDERS
# -------------------------
for f in ["scores","feedback","inbox","teacher_codes"]:
    os.makedirs(f, exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
for key in ["learner_name","teacher_logged_in","editor_logged_in","special_verified"]:
    if key not in st.session_state:
        st.session_state[key] = False

# -------------------------
# WELCOME PAGE
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
# SIDEBAR
# -------------------------
st.sidebar.title("Login")
user_type = st.sidebar.radio("I am:", ["Learner","Teacher","Editor"])

color_blind = st.sidebar.checkbox("🎨 Color-Blind Mode")
COLORS = {"A":"black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

# -------------------------
# TEACHER LOGIN / CODE PERSISTENCE
# -------------------------
if user_type=="Teacher":
    st.header("Teacher Section")
    teacher_name = st.text_input("Teacher Name")
    teacher_pwd = st.text_input("Password", type="password")
    if st.button("Login/Register"):
        if teacher_name and teacher_pwd:
            st.session_state.teacher_logged_in = True
            st.success(f"Welcome {teacher_name}!")

            # Persistent code
            code_file = f"teacher_codes/{teacher_name}.json"
            if os.path.exists(code_file):
                with open(code_file,"r") as f:
                    teacher_data = json.load(f)
                teacher_code = teacher_data["teacher_code"]
            else:
                teacher_code = str(uuid.uuid4())[:6].upper()
                with open(code_file,"w") as f:
                    json.dump({"teacher_code":teacher_code,"name":teacher_name,"date":str(datetime.now())},f)
            
            st.info(f"Your Teacher Code: **{teacher_code}** (Give this to your learners)")

            # Feedback area
            st.subheader("💡 Send Suggestion")
            suggestion = st.text_area("Suggestion to Editor")
            if st.button("Submit Suggestion"):
                fb_file = "feedback/feedback.json"
                fb_data = []
                if os.path.exists(fb_file):
                    with open(fb_file,"r") as f:
                        fb_data = json.load(f)
                fb_data.append({"role":"Teacher","suggestion":suggestion,"teacher":teacher_name})
                with open(fb_file,"w") as f:
                    json.dump(fb_data,f)
                st.success("Sent to editor!")

# -------------------------
# LEARNER LOGIN
# -------------------------
elif user_type=="Learner":
    learner_name = st.sidebar.text_input("Learner Name")
    teacher_code_input = st.sidebar.text_input("Teacher Code").strip()
    
    if st.sidebar.button("Login"):
        valid = False
        for file in os.listdir("teacher_codes"):
            with open(f"teacher_codes/{file}") as f:
                tdata = json.load(f)
                if teacher_code_input == tdata["teacher_code"]:
                    valid = True
                    st.session_state.teacher_name = tdata["name"]
                    break
        if valid:
            st.session_state.learner_name = learner_name
            st.success(f"Welcome {learner_name}! Linked to teacher {st.session_state.teacher_name}")
        else:
            st.error("Invalid Code! Ask your teacher for the correct code.")

# -------------------------
# LEARNER SECTION
# -------------------------
if user_type=="Learner" and st.session_state.learner_name:
    file = f"scores/{st.session_state.learner_name}.json"
    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
    else:
        data = {"pre_test":{},"post_test":{},"general_test":{},"simulations":{},"teacher":st.session_state.teacher_name}
        with open(file,"w") as f:
            json.dump(data,f)

    # ✅ Safe check to avoid KeyError
    pre_done = bool(data.get("pre_test", {}))
    post_done = bool(data.get("post_test", {}))

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
        st.header("📝 Pre-Test (Hard Questions, No Multiple Choices)")

        answers = {}
        # Example of 15 hard questions
        questions = [
            ("LCM of 14 and 35?", 70),
            ("GCD of 120 and 210?", 30),
            ("Simplify 150:200", "3:4"),
            ("x + y = 25, x - y = 5 → x?", 15),
            ("LCM of 18 and 24?", 72),
            ("GCD of 36 and 60?", 12),
            ("Simplify 45:60", "3:4"),
            ("x + y = 14, x - y = 2 → x?", 8),
            ("LCM of 21 and 28?", 84),
            ("GCD of 48 and 64?", 16),
            ("Simplify 36:48", "3:4"),
            ("x + y = 18, x - y = 4 → x?", 11),
            ("LCM of 20 and 30?", 60),
            ("GCD of 56 and 98?", 14),
            ("x + y = 10, x - y = 2 → y?", 4),
        ]

        for i, (q, _) in enumerate(questions):
            answers[i] = st.number_input(f"Q{i+1}: {q}", value=0)

        if st.button("Submit Pre-Test"):
            data["pre_test"] = {str(i): ans for i, ans in enumerate([a[1] for a in questions])}
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Pre-Test submitted! ✅")

    # -------------------------
    # POST TEST
    # -------------------------
    elif activity=="Post-Test":
        st.header("📝 Post-Test (Simulation Allowed)")

        # User feeds numbers into simulations
        a = st.number_input("Number A for LCM & GCD",1,100,6)
        b = st.number_input("Number B for LCM & GCD",1,100,8)
        lcm = a*b//math.gcd(a,b)
        gcd = math.gcd(a,b)

        val1 = st.number_input("Value A for Ratio",1,100,4)
        val2 = st.number_input("Value B for Ratio",1,100,6)
        frac = Fraction(val1,val2)

        a1 = st.number_input("a1 for SimEq",2)
        b1 = st.number_input("b1 for SimEq",3)
        c1 = st.number_input("c1 for SimEq",11)
        a2 = st.number_input("a2 for SimEq",1)
        b2 = st.number_input("b2 for SimEq",-1)
        c2 = st.number_input("c2 for SimEq",1)

        if st.button("Submit Post-Test"):
            data["post_test"] = {
                "LCM": lcm,
                "GCD": gcd,
                "Ratio": f"{frac.numerator}:{frac.denominator}",
                "SimEq": {"eq1":[a1,b1,c1],"eq2":[a2,b2,c2]}
            }
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Post-Test submitted! ✅")

            # Improvement graph for all
            labels = ["LCM","GCD","Ratio","SimEq"]
            pre_vals = [
                int(data.get("pre_test",{}).get("0",0)),
                int(data.get("pre_test",{}).get("1",0)),
                0,
                0
            ]
            post_vals = [lcm,gcd,frac.numerator/frac.denominator,1]  # SimEq treated as 1 for graph
            fig, ax = plt.subplots()
            ax.bar(np.arange(len(labels))-0.15, pre_vals, width=0.3,label="Pre-Test", color="red")
            ax.bar(np.arange(len(labels))+0.15, post_vals, width=0.3,label="Post-Test", color="green")
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels)
            ax.set_ylabel("Values / Scores")
            ax.legend()
            st.pyplot(fig)

    # -------------------------
    # SIMULATIONS
    # -------------------------
    elif activity=="Simulations":
        st.header("🔬 Simulations")
        topic = st.selectbox("Choose Topic", ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"])

        if topic=="LCM & GCD":
            a = st.number_input("A",2,50)
            b = st.number_input("B",2,50)
            gcd = math.gcd(a,b)
            lcm = a*b//gcd

            factors_a = [i for i in range(1,a+1) if a%i==0]
            factors_b = [i for i in range(1,b+1) if b%i==0]
            multiples_a = [a*i for i in range(1,6)]
            multiples_b = [b*i for i in range(1,6)]

            st.write("Factors A:", factors_a)
            st.write("Factors B:", factors_b)
            st.write("Multiples A:", multiples_a)
            st.write("Multiples B:", multiples_b)
            st.success(f"GCD={gcd}, LCM={lcm}")

            # Visualize
            fig, ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a), label="Factors A", color=COLORS["A"])
            ax.scatter(factors_b,[2]*len(factors_b), label="Factors B", color=COLORS["B"])
            ax.scatter(multiples_a,[1.5]*len(multiples_a), label="Multiples A", color=COLORS["C"])
            ax.scatter(multiples_b,[2.5]*len(multiples_b), label="Multiples B", color=COLORS["D"])
            for i,val in enumerate(factors_a): ax.text(val,1,str(val))
            for i,val in enumerate(factors_b): ax.text(val,2,str(val))
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        elif topic=="Simultaneous Equations":
            a1 = st.number_input("a1",2)
            b1 = st.number_input("b1",3)
            c1 = st.number_input("c1",11)
            a2 = st.number_input("a2",1)
            b2 = st.number_input("b2",-1)
            c2 = st.number_input("c2",1)

            st.latex(f"{a1}x + {b1}y = {c1}")
            st.latex(f"{a2}x + {b2}y = {c2}")

            if st.button("Solve Equations"):
                det = a1*b2 - a2*b1
                if det != 0:
                    x = (c1*b2 - c2*b1)/det
                    y = (a1*c2 - a2*c1)/det
                    st.success(f"Intersection at x={x}, y={y}")

                    # Graph with intersection point
                    x_vals = np.linspace(min(x-5,0), max(x+5,10),400)
                    y1_vals = (c1 - a1*x_vals)/b1
                    y2_vals = (c2 - a2*x_vals)/b2
                    fig, ax = plt.subplots()
                    ax.plot(x_vals, y1_vals, color=COLORS["A"], label="Eq1")
                    ax.plot(x_vals, y2_vals, color=COLORS["B"], label="Eq2")
                    ax.scatter(x,y,color=COLORS["D"],s=200,label="Intersection")
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.error("No solution exists")

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
