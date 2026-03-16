import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re
import smtplib
from email.message import EmailMessage
import json

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(
    page_title="Interactive Math Hub",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Interactive Math Hub")

# -------------------------
# PASSWORD STORAGE FILE
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher"])

# -------------------------
# LEARNER SECTION
# -------------------------
if user_type == "Learner":
    st.header("Learner Section")
    st.write("Welcome! Choose a topic from the sidebar to explore.")

    # Built-in topics
    default_topics = {
        "LCM & GCD": "built-in",
        "Prime Factors": "built-in",
        "Ratios": "built-in",
        "Simultaneous Equations": "built-in"
    }

    # Load dynamic topics
    dynamic_topics = {}
    if os.path.exists("topics"):
        for f in glob.glob("topics/*.py"):
            name = os.path.basename(f).replace("_", " ").replace(".py", "")
            dynamic_topics[name] = f

    all_topics = list(default_topics.keys()) + list(dynamic_topics.keys())
    tool = st.sidebar.selectbox("Choose Topic", all_topics)

    # Execute topic code
    if tool in dynamic_topics:
        st.subheader(f"Dynamic Topic: {tool}")
        topic_file = dynamic_topics[tool]
        with open(topic_file, "r") as f:
            code = f.read()
        exec(code)

    else:
        # BUILT-IN TOPICS
        if tool == "LCM & GCD":
            st.header("LCM & GCD Visualizer")
            a = st.number_input("Number 1", 1, 50, 6)
            b = st.number_input("Number 2", 1, 50, 8)
            gcd = math.gcd(a, b)
            lcm = a * b // gcd
            st.success(f"GCD = {gcd}")
            st.success(f"LCM = {lcm}")

            st.subheader("Factors & Multiples")
            factors_a = [i for i in range(1, a+1) if a % i == 0]
            factors_b = [i for i in range(1, b+1) if b % i == 0]
            multiples_a = [a*i for i in range(1, 10)]
            multiples_b = [b*i for i in range(1, 10)]

            colorblind = st.checkbox("Enable color-blind friendly mode")

            fig, ax = plt.subplots()
            y_positions = [1,2,3,4]
            ax.scatter(factors_a, [y_positions[0]]*len(factors_a),
                       marker="s", color="orange" if not colorblind else "black", label="Factors A")
            ax.scatter(factors_b, [y_positions[1]]*len(factors_b),
                       marker="s", color="blue" if not colorblind else "gray", label="Factors B")
            ax.scatter(multiples_a, [y_positions[2]]*len(multiples_a),
                       marker="o", color="green" if not colorblind else "purple", label="Multiples A")
            ax.scatter(multiples_b, [y_positions[3]]*len(multiples_b),
                       marker="o", color="red" if not colorblind else "brown", label="Multiples B")
            ax.scatter(lcm, 2.5, color="green" if not colorblind else "purple", s=120, label="LCM")
            ax.scatter(gcd, 0.5, color="orange" if not colorblind else "black", s=120, label="GCD")

            for x in factors_a: ax.text(x,1.05,str(x),ha="center")
            for x in factors_b: ax.text(x,2.05,str(x),ha="center")
            for x in multiples_a: ax.text(x,3.05,str(x),ha="center")
            for x in multiples_b: ax.text(x,4.05,str(x),ha="center")

            ax.set_yticks([0.5,1,2,3,4,2.5])
            ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

        elif tool == "Prime Factors":
            st.header("Prime Factorization")
            num = int(st.number_input("Enter number", value=24))
            def prime_factors(n):
                factors = []
                d = 2
                while n > 1:
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                    d += 1
                return factors
            if st.button("Find Prime Factors"):
                factors = prime_factors(num)
                st.success(f"Prime Factors: {factors}")

        elif tool == "Ratios":
            st.header("Ratio Simplifier")
            a = st.number_input("First Number", value=4)
            b = st.number_input("Second Number", value=8)
            if st.button("Simplify Ratio"):
                g = math.gcd(a,b)
                st.success(f"Simplified Ratio = {int(a/g)} : {int(b/g)}")

        elif tool == "Simultaneous Equations":
            st.header("Simple Simultaneous Equation Solver")
            eq1 = st.text_input("Equation 1", "2x + 3y = 11")
            eq2 = st.text_input("Equation 2", "1x - 1y = 1")
            def parse_eq(eq):
                numbers = list(map(int, re.findall(r'-?\d+', eq)))
                return numbers[0], numbers[1], numbers[2]
            if st.button("Solve Equations"):
                try:
                    a1,b1,c1 = parse_eq(eq1)
                    a2,b2,c2 = parse_eq(eq2)
                    det = a1*b2 - a2*b1
                    if det != 0:
                        x = (c1*b2 - c2*b1)/det
                        y = (a1*c2 - a2*c1)/det
                        st.success(f"Solution: x = {x}, y = {y}")
                        # Graph
                        x_vals = np.linspace(-10,10,400)
                        y1 = (c1 - a1*x_vals)/b1
                        y2 = (c2 - a2*x_vals)/b2
                        fig,ax = plt.subplots()
                        ax.plot(x_vals,y1,label="Equation 1")
                        ax.plot(x_vals,y2,label="Equation 2")
                        ax.scatter(x,y,color="red",s=100,label="Solution")
                        ax.grid(True)
                        ax.legend()
                        st.pyplot(fig)
                    else:
                        st.error("No unique solution exists!")
                except:
                    st.error("Error parsing equations. Use format ax + by = c.")

# -------------------------
# TEACHER SECTION WITH EDITOR APPROVAL
# -------------------------
elif user_type == "Teacher":
    st.header("Teacher Section")
    st.write("Submit a new math topic. Requires editor approval.")

    # Teacher login / registration
    action = st.radio("Login or Register", ["Login", "Register"])
    teacher_name = st.text_input("Teacher Username")
    teacher_password = st.text_input("Password", type="password")

    if action == "Register" and st.button("Register"):
        if teacher_name in teacher_data:
            st.error("Username exists. Choose another.")
        else:
            teacher_data[teacher_name] = teacher_password
            with open(PASSWORD_FILE, "w") as f:
                json.dump(teacher_data, f)
            st.success("Registered successfully!")

    elif action == "Login" and st.button("Login"):
        if teacher_name in teacher_data and teacher_data[teacher_name] == teacher_password:
            st.success("Login successful! Submit topics below.")

            topic_name = st.text_input("Topic Name")
            topic_description = st.text_area("Topic Description")
            topic_code = st.text_area("Topic Code")

            editor_password = st.text_input("Editor Approval Password", type="password")
            if st.button("Submit Topic for Approval"):
                if editor_password == "mercy paul i love you":  # Your master password
                    recipients = ["aleccleopatra7@gmail.com","alecriya22@gmail.com"]

                    msg = EmailMessage()
                    msg['Subject'] = f"New Topic Submitted: {topic_name}"
                    msg['From'] = "aleccleopatra7@gmail.com"
                    msg['To'] = ", ".join(recipients)
                    msg.set_content(f"Topic: {topic_name}\nDescription:\n{topic_description}\nCode:\n{topic_code}")

                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login("aleccleopatra7@gmail.com","aceluffy#")
                            smtp.send_message(msg)
                        st.success("Topic submitted and emailed to editor!")
                    except Exception as e:
                        st.error(f"Failed to send email: {e}")
                else:
                    st.error("Invalid editor password. Submission blocked.")
        else:
            st.error("Invalid teacher login.")
