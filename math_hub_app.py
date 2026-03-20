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
            # Generate unique teacher code
            teacher_code = str(uuid.uuid4())[:6].upper()
            code_file = f"teacher_codes/{teacher_name}.json"
            with open(code_file,"w") as f:
                json.dump({"teacher_code":teacher_code,"name":teacher_name,"date":str(datetime.now())},f)
            st.info(f"Your Teacher Code: **{teacher_code}** (Give this to your learners)")

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

    pre_done = bool(data.get("pre_test"))
    post_done = bool(data.get("post_test"))

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
        st.header("📝 Pre-Test (No Simulation)")
        answers = {}
        answers["LCM"] = st.radio("LCM of 12 and 18?", [36,54,72,24])
        answers["GCD"] = st.radio("GCD of 24 and 36?", [12,6,18,24])
        answers["Ratio"] = st.radio("Simplify 12:18", ["2:3","3:4","2:2","4:6"])
        answers["SimEq"] = st.radio("Solve x+y=4, x-y=2 → x?", [1,2,3,4])

        if st.button("Submit Pre-Test"):
            data["pre_test"] = answers
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Pre-Test submitted! ✅")
            
            # Step-by-step display
            st.subheader("Step-by-Step Solutions:")
            st.write("**LCM:** 12 → [1,2,3,4,6,12], 18 → [1,2,3,6,9,18], LCM = 36")
            st.write("**GCD:** Common factors: [1,2,3,6], GCD = 12")
            st.write("**Ratio:** 12:18 → Simplify by GCD 6 → 2:3")
            st.write("**SimEq:** x+y=4, x-y=2 → Solve: x=(4+2)/2=3, y=1")

    # -------------------------
    # POST TEST
    # -------------------------
    elif activity=="Post-Test":
        st.header("📝 Post-Test (Simulations Allowed)")

        # LCM & GCD
        a = st.number_input("Number A for LCM & GCD",1,100,6)
        b = st.number_input("Number B for LCM & GCD",1,100,8)
        gcd = math.gcd(a,b)
        lcm = a*b//gcd

        # Prime factors
        n = st.number_input("Number for Prime Factorization",2,100,12)
        temp = n
        i=2
        tree=[]
        while temp>1:
            if temp%i==0:
                tree.append((temp,i,temp//i))
                temp//=i
            else:
                i+=1

        # Ratios
        val1 = st.number_input("Value A for Ratio",1,100,4)
        val2 = st.number_input("Value B for Ratio",1,100,6)
        frac = Fraction(val1,val2)

        # Simultaneous equations
        a1 = st.number_input("a1",2)
        b1 = st.number_input("b1",3)
        c1 = st.number_input("c1",11)
        a2 = st.number_input("a2",1)
        b2 = st.number_input("b2",-1)
        c2 = st.number_input("c2",1)

        if st.button("Submit Post-Test"):
            data["post_test"] = {
                "LCM":lcm,"GCD":gcd,"PrimeFactors":tree,"Ratio":f"{frac.numerator}:{frac.denominator}",
                "SimEq":{"eq1":[a1,b1,c1],"eq2":[a2,b2,c2]}
            }
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Post-Test submitted! ✅")

            # Step-by-step
            st.subheader("Step-by-Step Solutions:")
            st.write(f"**LCM:** gcd({a},{b})={gcd} → lcm({a},{b})={lcm}")
            st.write(f"**Prime Factors of {n}:** {tree}")
            st.write(f"**Ratio:** {val1}:{val2} → {frac.numerator}:{frac.denominator}")
            det = a1*b2 - a2*b1
            if det != 0:
                x = (c1*b2 - c2*b1)/det
                y = (a1*c2 - a2*c1)/det
                st.write(f"**Simultaneous Equations:** x={x}, y={y}")
            else:
                st.write("**Simultaneous Equations:** No solution")

            # Improvement Graph
            pre_vals = [int(data.get("pre_test",{}).get("LCM",0)),int(data.get("pre_test",{}).get("GCD",0)),0,0]
            post_vals = [lcm,gcd,0,0]
            labels = ["LCM","GCD","Ratio","SimEq"]
            fig,ax = plt.subplots()
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

            if st.button("Show Step-by-Step LCM & GCD"):
                st.subheader("Step-by-Step Factors & LCM/GCD")
                st.write(f"Factors of A ({a}): {factors_a}")
                st.write(f"Factors of B ({b}): {factors_b}")
                st.write(f"GCD calculation: gcd({a},{b}) = {gcd}")
                st.write(f"LCM calculation: lcm({a},{b}) = {lcm}")

            fig,ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a), label="Factors A", color=COLORS["A"])
            ax.scatter(factors_b,[2]*len(factors_b), label="Factors B", color=COLORS["B"])
            ax.scatter(multiples_a,[1.5]*len(multiples_a), label="Multiples A", color=COLORS["C"])
            ax.scatter(multiples_b,[2.5]*len(multiples_b), label="Multiples B", color=COLORS["D"])
            for i,val in enumerate(factors_a): ax.text(val,1,str(val))
            for i,val in enumerate(factors_b): ax.text(val,2,str(val))
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        # Ratio Step-by-Step
        elif topic=="Ratios":
            val1 = st.number_input("Value A",1,100,4)
            val2 = st.number_input("Value B",1,100,6)
            frac = Fraction(val1,val2)
            st.success(f"Simplified Ratio: {frac.numerator}:{frac.denominator}")
            if st.button("Show Step-by-Step Ratio"):
                st.subheader("Step-by-Step Simplification")
                st.write(f"Original Ratio: {val1}:{val2}")
                st.write(f"GCD of {val1} and {val2} is {math.gcd(val1,val2)}")
                st.write(f"Simplified: {frac.numerator}:{frac.denominator}")

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

            if st.button("Solve Equations Step-by-Step"):
                det = a1*b2 - a2*b1
                if det !=0:
                    x = (c1*b2 - c2*b1)/det
                    y = (a1*c2 - a2*c1)/det
                    st.success(f"Intersection at x={x}, y={y}")

                    st.subheader("Step-by-Step Solution")
                    st.write("Using Determinant Method:")
                    st.write(f"x = (c1*b2 - c2*b1)/det = ({c1}*{b2} - {c2}*{b1})/{det} = {x}")
                    st.write(f"y = (a1*c2 - a2*c1)/det = ({a1}*{c2} - {a2}*{c1})/{det} = {y}")

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
