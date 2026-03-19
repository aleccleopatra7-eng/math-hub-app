import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from fractions import Fraction
import pandas as pd

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")
st.title("📊 Interactive Math Hub")

# -------------------------
# COLOR-BLIND MODE
# -------------------------
color_blind = st.checkbox("🎨 Enable Color-Blind Mode")
COLORS = {"A":"black","B":"gray","C":"blue","D":"purple"} if color_blind else {"A":"orange","B":"blue","C":"green","D":"red"}

# -------------------------
# CREATE FOLDERS
# -------------------------
folders = ["submissions","approved","inbox","feedback","scores"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
for key in ["teacher_logged_in","editor_logged_in","special_verified","pre_completed","post_completed","pre_scores","post_scores"]:
    if key not in st.session_state:
        st.session_state[key] = False if "logged" in key or "completed" in key or "special_verified" in key else {}

# -------------------------
# LOAD TEACHERS
# -------------------------
if os.path.exists("teachers.json"):
    with open("teachers.json","r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# EDITOR PASSWORD
# -------------------------
EDITOR_PASSWORD = "alex"

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner","Teacher","Editor"])
topics = ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"]

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type=="Learner":
    st.header("Learner Section")

    name = st.text_input("Enter your name")
    teacher_code = st.text_input("Enter your Teacher Code")

    if name and teacher_code:

        # -------------------------
        # PRE-TEST
        # -------------------------
        if not st.session_state.pre_completed:
            st.subheader("Pre-Test (Simulations Locked)")
            pre_answers = {}
            for topic in topics:
                st.markdown(f"**{topic} Questions**")
                if topic=="LCM & GCD":
                    pre_answers[topic] = st.radio("LCM of 6 and 8?", [12,24,48,14], key=f"pre_{topic}")
                elif topic=="Prime Factors":
                    pre_answers[topic] = st.radio("Prime factors of 12?", ["2,2,3","2,3,6","3,4","2,3,4"], key=f"pre_{topic}")
                elif topic=="Ratios":
                    pre_answers[topic] = st.radio("Simplify ratio 8:12?", ["2:3","3:2","4:6","2:5"], key=f"pre_{topic}")
                elif topic=="Simultaneous Equations":
                    pre_answers[topic] = st.radio("Solve x+y=4, x-y=2?", ["x=3,y=1","x=2,y=2","x=1,y=3","x=4,y=0"], key=f"pre_{topic}")

            if st.button("Submit Pre-Test"):
                correct={"LCM & GCD":24,"Prime Factors":"2,2,3","Ratios":"2:3","Simultaneous Equations":"x=3,y=1"}
                scores={t:1 if pre_answers[t]==correct[t] else 0 for t in topics}
                st.session_state.pre_scores = scores
                st.session_state.pre_completed=True

                with open(f"scores/{name}_pre.json","w") as f:
                    json.dump(scores,f)

                inbox_file=f"inbox/{teacher_code}.json"
                inbox_data=[]
                if os.path.exists(inbox_file):
                    with open(inbox_file,"r") as f:
                        inbox_data=json.load(f)
                inbox_data.append({"name":name,"type":"pre-test","scores":scores})
                with open(inbox_file,"w") as f:
                    json.dump(inbox_data,f)
                st.success("Pre-Test completed! Scores sent to teacher. Simulations still locked.")

        # -------------------------
        # POST-TEST & SIMULATION TOGGLE
        # -------------------------
        elif st.session_state.pre_completed:
            st.subheader("Post-Test & Simulations Access")
            post_answers = {}
            for topic in topics:
                st.markdown(f"**{topic} Questions**")
                if topic=="LCM & GCD":
                    post_answers[topic]=st.radio("LCM of 10 and 15?", [30,20,15,25], key=f"post_{topic}")
                elif topic=="Prime Factors":
                    post_answers[topic]=st.radio("Prime factors of 18?", ["2,3,3","2,9","3,6","2,2,5"], key=f"post_{topic}")
                elif topic=="Ratios":
                    post_answers[topic]=st.radio("Simplify ratio 14:21?", ["2:3","3:2","7:10","14:21"], key=f"post_{topic}")
                elif topic=="Simultaneous Equations":
                    post_answers[topic]=st.radio("Solve x+y=5, x-y=1?", ["x=3,y=2","x=2,y=3","x=4,y=1","x=1,y=4"], key=f"post_{topic}")

            if st.button("Submit Post-Test"):
                correct={"LCM & GCD":30,"Prime Factors":"2,3,3","Ratios":"2:3","Simultaneous Equations":"x=3,y=2"}
                scores={t:1 if post_answers[t]==correct[t] else 0 for t in topics}
                st.session_state.post_scores=scores
                st.session_state.post_completed=True

                with open(f"scores/{name}_post.json","w") as f:
                    json.dump(scores,f)

                inbox_file=f"inbox/{teacher_code}.json"
                inbox_data=[]
                if os.path.exists(inbox_file):
                    with open(inbox_file,"r") as f:
                        inbox_data=json.load(f)
                inbox_data.append({"name":name,"type":"post-test","scores":scores})
                with open(inbox_file,"w") as f:
                    json.dump(inbox_data,f)

                # Calculate improvement
                improvements={t:(scores[t]-st.session_state.pre_scores[t])*100 for t in topics}
                st.success("Post-Test completed! Simulations unlocked.")
                st.balloons()

                # Show results table
                data = []
                for t in topics:
                    pre_score = st.session_state.pre_scores[t]
                    post_score = scores[t]
                    improvement = post_score - pre_score
                    data.append([t, pre_score, post_score, improvement])
                df = pd.DataFrame(data, columns=["Topic","Pre-Test Score","Post-Test Score","Improvement"])
                st.subheader("📊 Pre-Test vs Post-Test Results")
                st.table(df)

            # -------------------------
            # Simulation Toggle
            # -------------------------
            if st.session_state.post_completed:
                st.markdown("### ✅ Choose Simulation Topics")
                selected_topics=st.multiselect("Select simulations to run",topics)

                if "LCM & GCD" in selected_topics:
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

                if "Prime Factors" in selected_topics:
                    st.subheader("Prime Factorization Tree")
                    n = st.number_input("Enter number",2,100,12,key="prime_tree")
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

                if "Ratios" in selected_topics:
                    st.subheader("Simplified Ratios")
                    a = st.number_input("Value A",1,100,4,key="ratio_a")
                    b = st.number_input("Value B",1,100,6,key="ratio_b")
                    frac = Fraction(a,b)
                    st.success(f"{a}:{b} → {frac.numerator}:{frac.denominator}")

                if "Simultaneous Equations" in selected_topics:
                    st.subheader("Simultaneous Equation Solver")
                    a1 = st.number_input("a1", value=2,key="sim_a1")
                    b1 = st.number_input("b1", value=3,key="sim_b1")
                    c1 = st.number_input("c1", value=11,key="sim_c1")
                    a2 = st.number_input("a2", value=1,key="sim_a2")
                    b2 = st.number_input("b2", value=-1,key="sim_b2")
                    c2 = st.number_input("c2", value=1,key="sim_c2")
                    if st.button("Solve Equations"):
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
        st.subheader("📬 Student Requests & Test Results")
        inbox_file=f"inbox/{code}.json"
        if os.path.exists(inbox_file):
            with open(inbox_file,"r") as f:
                data=json.load(f)
            for d in data:
                st.write(d["name"],"-",d["type"])
                st.write(d["scores"])
                st.write("------")
        else:
            st.info("No student results yet.")
        st.subheader("💡 Teacher Suggestions")
        suggestion = st.text_area("Give a suggestion to improve the system")
        if st.button("Submit Suggestion"):
            file="feedback/feedback.json"
            data=[]
            if os.path.exists(file):
                with open(file,"r") as f:
                    data=json.load(f)
            data.append({"role":"Teacher","rating":None,"comment":"","suggestion":suggestion})
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Suggestion sent to Editor!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type=="Editor":
    st.header("Editor Section")
    password=st.text_input("Enter Password",type="password")
    if password==EDITOR_PASSWORD:
        st.session_state.editor_logged_in=True
    if st.session_state.editor_logged_in:
        st.success("Access Granted")
        st.subheader("⭐ All Feedback (Editor Only)")
        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
            for d in data:
                st.write("Role:",d["role"])
                st.write("Rating:",d["rating"])
                st.write("Comment:",d["comment"])
                st.write("Suggestion:",d["suggestion"])
                st.write("------")
        else:
            st.info("No feedback yet")
        if not st.session_state.special_verified:
            st.subheader("🔐 Answer to Access Games")
            answer=st.text_input("who is my chizi?")
            if st.button("Submit Answer"):
                if answer.lower().strip()=="riya":
                    st.session_state.special_verified=True
                    st.success("Access granted 🎮")
                else:
                    st.error("Wrong answer")
        else:
            st.subheader("🎮 Mini Games")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
