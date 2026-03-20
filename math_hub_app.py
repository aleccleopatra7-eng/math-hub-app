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
# SIDEBAR
# -------------------------
st.sidebar.title("Login")
user_type = st.sidebar.radio("I am:", ["Learner","Teacher","Editor"])
color_blind = st.sidebar.checkbox("🎨 Color-Blind Mode")
COLORS = {"A":"black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

# -------------------------
# WELCOME PAGE
# -------------------------
st.markdown("""
<h1 style='text-align:center; color:orange; animation: fadeIn 2s;'>
🎉 Welcome to My Math Interactive Hub
</h1>
<p style='text-align:center;'>Learn, Practice, and Improve your Math skills!</p>
<style>
@keyframes fadeIn {
    from {opacity: 0; transform: scale(0.5);}
    to {opacity: 1; transform: scale(1);}
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# TEACHER LOGIN / CODE GENERATION
# -------------------------
if user_type=="Teacher":
    st.header("Teacher Section")
    teacher_name = st.text_input("Teacher Name")
    teacher_pwd = st.text_input("Password", type="password")
    
    if st.button("Login/Register"):
        if teacher_name and teacher_pwd:
            st.session_state.teacher_logged_in = True
            st.success(f"Welcome {teacher_name}!")

            # Persistent teacher code
            code_file = f"teacher_codes/{teacher_name}.json"
            if os.path.exists(code_file):
                with open(code_file,"r") as f:
                    tdata = json.load(f)
                    teacher_code = tdata["teacher_code"]
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

    pre_done = bool(data["pre_test"])
    post_done = bool(data["post_test"])
    general_done = bool(data["general_test"])

    options = ["Simulations"]
    if not pre_done:
        options += ["Pre-Test"]
    if not post_done:
        options += ["Post-Test"]
    if pre_done and post_done:
        options += ["General Test"]

    activity = st.sidebar.radio("Activities", options)

    # -------------------------
    # PRE TEST (Hard Questions, 15)
    # -------------------------
    if activity=="Pre-Test":
        st.header("📝 Pre-Test (Hard, No Multiple Choice)")
        answers = {}
        for i in range(1,16):
            q = st.number_input(f"Question {i}: Enter your answer",value=0,key=f"pre{i}")
            answers[f"Q{i}"] = q
        if st.button("Submit Pre-Test"):
            data["pre_test"] = answers
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Pre-Test submitted! ✅")

    # -------------------------
    # POST TEST (Simulation Usage)
    # -------------------------
    elif activity=="Post-Test":
        st.header("📝 Post-Test (Simulations Allowed)")

        st.subheader("LCM & GCD")
        a = st.number_input("Number A",1,50,key="postA")
        b = st.number_input("Number B",1,50,key="postB")
        lcm = a*b//math.gcd(a,b)
        gcd = math.gcd(a,b)
        st.write("Use simulation if needed!")

        st.subheader("Ratios")
        val1 = st.number_input("Value A",1,50,key="postR1")
        val2 = st.number_input("Value B",1,50,key="postR2")
        frac = Fraction(val1,val2)

        st.subheader("Simultaneous Equations")
        a1 = st.number_input("a1",1,key="posta1")
        b1 = st.number_input("b1",1,key="postb1")
        c1 = st.number_input("c1",1,key="postc1")
        a2 = st.number_input("a2",1,key="posta2")
        b2 = st.number_input("b2",1,key="postb2")
        c2 = st.number_input("c2",1,key="postc2")

        if st.button("Submit Post-Test"):
            data["post_test"] = {
                "LCM":lcm,"GCD":gcd,
                "Ratio":f"{frac.numerator}:{frac.denominator}",
                "SimEq":{"eq1":[a1,b1,c1],"eq2":[a2,b2,c2]}
            }
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Post-Test submitted ✅")

            # Improvement Graph
            labels = ["LCM","GCD","Ratio","SimEq"]
            pre_vals = [0]*4
            if data.get("pre_test"):
                # assume pre-test values if exist
                pre_vals = [data["pre_test"].get(f"Q{i}",0) for i in range(1,5)]
            post_vals = [lcm,gcd,frac.numerator,1]  # SimEq placeholder
            fig,ax=plt.subplots()
            ax.bar(np.arange(len(labels))-0.15, pre_vals, width=0.3,label="Pre-Test",color="red")
            ax.bar(np.arange(len(labels))+0.15, post_vals, width=0.3,label="Post-Test",color="green")
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels)
            ax.set_ylabel("Scores / Values")
            ax.legend()
            st.pyplot(fig)

    # -------------------------
    # GENERAL TEST (After Post-Test)
    # -------------------------
    elif activity=="General Test":
        st.header("📝 General Test (All Topics, Use Simulation)")

        # LCM & GCD
        a = st.number_input("Number A",2,50,key="genA")
        b = st.number_input("Number B",2,50,key="genB")
        gcd_val = math.gcd(a,b)
        lcm_val = a*b//gcd_val
        st.write("Use simulation below if needed!")

        # Ratios
        r1 = st.number_input("Value A",1,100,key="genR1")
        r2 = st.number_input("Value B",1,100,key="genR2")
        frac_val = Fraction(r1,r2)

        # Simultaneous Equations
        a1 = st.number_input("a1",2,key="gena1")
        b1 = st.number_input("b1",3,key="genb1")
        c1 = st.number_input("c1",11,key="genc1")
        a2 = st.number_input("a2",1,key="gena2")
        b2 = st.number_input("b2",-1,key="genb2")
        c2 = st.number_input("c2",1,key="genc2")

        if st.button("Submit General Test"):
            data["general_test"] = {
                "LCM":lcm_val,"GCD":gcd_val,
                "Ratio":f"{frac_val.numerator}:{frac_val.denominator}",
                "SimEq":{"eq1":[a1,b1,c1],"eq2":[a2,b2,c2]}
            }
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("General Test submitted ✅")

            # Update Improvement Graph to include general test
            labels = ["LCM","GCD","Ratio","SimEq"]
            pre_vals = [data["pre_test"].get(f"Q{i}",0) for i in range(1,5)]
            post_vals = [data["post_test"]["LCM"],data["post_test"]["GCD"],1,1]  # placeholder for simplicity
            gen_vals = [lcm_val,gcd_val,frac_val.numerator,1]
            fig,ax=plt.subplots()
            ax.bar(np.arange(len(labels))-0.2, pre_vals,width=0.2,label="Pre-Test",color="red")
            ax.bar(np.arange(len(labels)), post_vals,width=0.2,label="Post-Test",color="green")
            ax.bar(np.arange(len(labels))+0.2, gen_vals,width=0.2,label="General Test",color="blue")
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels)
            ax.set_ylabel("Scores / Values")
            ax.legend()
            st.pyplot(fig)

    # -------------------------
    # SIMULATIONS
    # -------------------------
    elif activity=="Simulations":
        st.header("🔬 Simulations")
        topic = st.selectbox("Choose Topic", ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"])

        # LCM & GCD Visualizer
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

            # Plot
            fig,ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a), label="Factors A", color=COLORS["A"])
            ax.scatter(factors_b,[2]*len(factors_b), label="Factors B", color=COLORS["B"])
            ax.scatter(multiples_a,[1.5]*len(multiples_a), label="Multiples A", color=COLORS["C"])
            ax.scatter(multiples_b,[2.5]*len(multiples_b), label="Multiples B", color=COLORS["D"])
            for i,val in enumerate(factors_a):
                ax.text(val,1,str(val))
            for i,val in enumerate(factors_b):
                ax.text(val,2,str(val))
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        # Simultaneous Equations Solver
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
                if det !=0:
                    x = (c1*b2 - c2*b1)/det
                    y = (a1*c2 - a2*c1)/det
                    st.success(f"Intersection at x={x}, y={y}")

                    x_vals = np.linspace(min(x-5,0), max(x+5,10),400)
                    y1_vals = (c1 - a1*x_vals)/b1
                    y2_vals = (c2 - a2*x_vals)/b2
                    fig,ax = plt.subplots()
                    ax.plot(x_vals,y1_vals,color=COLORS["A"],label="Eq1")
                    ax.plot(x_vals,y2_vals,color=COLORS["B"],label="Eq2")
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
