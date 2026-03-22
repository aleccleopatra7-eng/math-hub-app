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
<h1 style='text-align:center; color:orange;'>
🎉 Welcome to My Math Interactive Hub
</h1>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Login")
user_type = st.sidebar.radio("I am:", ["Learner","Teacher","Editor"])

color_blind = st.sidebar.checkbox("🎨 Color-Blind Mode")
COLORS = {"A":"black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

# -------------------------
# TEACHER LOGIN
# -------------------------
if user_type=="Teacher":
    st.header("Teacher Section")
    teacher_name = st.text_input("Teacher Name")
    teacher_pwd = st.text_input("Password", type="password")

    if st.button("Login/Register"):
        if teacher_name and teacher_pwd:
            st.session_state.teacher_logged_in = True
            st.success(f"Welcome {teacher_name}!")

            file = f"teacher_codes/{teacher_name}.json"

            if os.path.exists(file):
                with open(file) as f:
                    data = json.load(f)
                code = data["teacher_code"]
            else:
                code = str(uuid.uuid4())[:6].upper()
                with open(file,"w") as f:
                    json.dump({"teacher_code":code},f)

            st.info(f"Your Teacher Code: {code}")

# -------------------------
# LEARNER LOGIN
# -------------------------
elif user_type=="Learner":
    learner_name = st.sidebar.text_input("Learner Name")
    teacher_code_input = st.sidebar.text_input("Teacher Code")

    if st.sidebar.button("Login"):
        valid = False
        for file in os.listdir("teacher_codes"):
            with open(f"teacher_codes/{file}") as f:
                tdata = json.load(f)
                if teacher_code_input == tdata["teacher_code"]:
                    valid = True
                    break

        if valid:
            st.session_state.learner_name = learner_name
            st.success(f"Welcome {learner_name}")
        else:
            st.error("Invalid Code")

# -------------------------
# LEARNER SYSTEM
# -------------------------
if user_type=="Learner" and st.session_state.learner_name:

    file = f"scores/{st.session_state.learner_name}.json"

    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
    else:
        data = {"pre_test":{}, "post_test":{}}
        with open(file,"w") as f:
            json.dump(data,f)

    pre_done = bool(data.get("pre_test",{}))
    post_done = bool(data.get("post_test",{}))

    options = ["Simulations"]
    if not pre_done or not post_done:
        options += ["Pre-Test","Post-Test"]
    else:
        options += ["General Test"]

    activity = st.sidebar.radio("Activities", options)

    # -------------------------
    # SIMULATIONS
    # -------------------------
    if activity=="Simulations":

        topic = st.selectbox("Choose Topic", ["LCM & GCD","Simultaneous Equations"])

        # -------------------------
        # LCM & GCD
        # -------------------------
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

            fig, ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a))
            ax.scatter(factors_b,[2]*len(factors_b))

            for val in factors_a:
                ax.text(val,1,str(val))
            for val in factors_b:
                ax.text(val,2,str(val))

            ax.grid(True)
            st.pyplot(fig)

        # -------------------------
        # SIMULTANEOUS EQUATIONS (UPGRADED)
        # -------------------------
        elif topic=="Simultaneous Equations":

            st.subheader("Solve using Elimination or Substitution")

            a1 = st.number_input("a1", value=2)
            b1 = st.number_input("b1", value=3)
            c1 = st.number_input("c1", value=11)

            a2 = st.number_input("a2", value=1)
            b2 = st.number_input("b2", value=-1)
            c2 = st.number_input("c2", value=1)

            method = st.radio("Choose Method", ["Elimination","Substitution"])

            st.latex(f"{a1}x + {b1}y = {c1}")
            st.latex(f"{a2}x + {b2}y = {c2}")

            if st.button("Solve"):

                det = a1*b2 - a2*b1

                if det == 0:
                    st.error("No unique solution")
                else:
                    x = (c1*b2 - c2*b1)/det
                    y = (a1*c2 - a2*c1)/det

                    # -------------------------
                    # ELIMINATION STEPS
                    # -------------------------
                    if method=="Elimination":
                        st.write("Step 1: Multiply equations to eliminate one variable")
                        st.write("Step 2: Subtract equations")
                        st.write("Step 3: Solve remaining variable")
                        st.write("Step 4: Substitute back")

                    # -------------------------
                    # SUBSTITUTION STEPS
                    # -------------------------
                    else:
                        st.write("Step 1: Make one variable subject")
                        st.write("Step 2: Substitute into other equation")
                        st.write("Step 3: Solve")
                        st.write("Step 4: Substitute back")

                    st.success(f"Solution: x = {x}, y = {y}")

                    # GRAPH
                    x_vals = np.linspace(x-10, x+10, 400)

                    if b1 != 0:
                        y1 = (c1 - a1*x_vals)/b1
                    else:
                        y1 = None

                    if b2 != 0:
                        y2 = (c2 - a2*x_vals)/b2
                    else:
                        y2 = None

                    fig, ax = plt.subplots()

                    if y1 is not None:
                        ax.plot(x_vals,y1,label="Eq1")
                    else:
                        ax.axvline(x=c1/a1,label="Eq1")

                    if y2 is not None:
                        ax.plot(x_vals,y2,label="Eq2")
                    else:
                        ax.axvline(x=c2/a2,label="Eq2")

                    ax.scatter(x,y,s=250)
                    ax.text(x,y,f"({x:.2f},{y:.2f})")

                    ax.legend()
                    ax.grid(True)
                    st.pyplot(fig)

# -------------------------
# EDITOR
# -------------------------
elif user_type=="Editor":
    st.header("Editor Section")
    password = st.text_input("Password", type="password")

    if password=="alex":
        st.success("Access Granted")

        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file) as f:
                data=json.load(f)
            for d in data:
                st.write(d)
