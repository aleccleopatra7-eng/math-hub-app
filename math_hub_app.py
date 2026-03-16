import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import openai
from github import Github
import os
import glob
import re

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(
    page_title="Interactive Math Hub",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Interactive Math Hub")

# Ensure 'topics' folder exists
os.makedirs("topics", exist_ok=True)

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.title("Navigation")
section = st.sidebar.selectbox("Select Section", ("Learner Section", "Teacher Section"))

# -------------------------
# LEARNER SECTION
# -------------------------
if section == "Learner Section":

    # Default built-in topics
    default_topics = {
        "LCM & GCD": "built-in",
        "Prime Factors": "built-in",
        "Ratios": "built-in",
        "Simultaneous Equations": "built-in"
    }

    # Load additional topics from 'topics/' folder dynamically
    dynamic_topics = {}
    for f in glob.glob("topics/*.py"):
        name = os.path.basename(f).replace("_", " ").replace(".py", "")
        dynamic_topics[name] = f

    # Combine built-in + dynamic topics
    all_topics = list(default_topics.keys()) + list(dynamic_topics.keys())
    tool = st.sidebar.selectbox("Choose Topic", all_topics)

    # -------------------------
    # EXECUTE TOPIC CODE
    # -------------------------
    if tool in dynamic_topics:
        st.subheader(f"Dynamic Topic: {tool}")
        topic_file = dynamic_topics[tool]
        with open(topic_file, "r") as f:
            code = f.read()
        exec(code)

    else:
        # -------------------------
        # BUILT-IN TOPICS
        # -------------------------
        if tool == "LCM & GCD":
            st.header("LCM & GCD Visualizer")
            a = st.slider("Select Number 1", 1, 50, 6)
            b = st.slider("Select Number 2", 1, 50, 8)
            gcd = math.gcd(a, b)
            lcm = a * b // gcd
            st.success(f"GCD = {gcd}")
            st.success(f"LCM = {lcm}")

            limit = max(a, b) * 8
            fig, ax = plt.subplots()
            ax.hlines(0, 0, limit)
            for i in range(a, limit, a):
                ax.scatter(i, 0.1)
                ax.text(i, 0.12, str(i), ha="center")
            for i in range(b, limit, b):
                ax.scatter(i, -0.1)
            ax.scatter(lcm, 0, s=200, label="LCM")
            ax.set_xlim(0, limit)
            ax.set_yticks([])
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
            if st.button("Simplify"):
                g = math.gcd(a, b)
                st.success(f"Simplified Ratio = {int(a/g)} : {int(b/g)}")

        elif tool == "Simultaneous Equations":
            st.header("Simple Simultaneous Equation Solver")
            st.write("Enter two equations in the form: `ax + by = c`")

            eq1 = st.text_input("Equation 1", "2x + 3y = 11")
            eq2 = st.text_input("Equation 2", "1x - 1y = 1")

            def parse_eq(eq):
                numbers = list(map(int, re.findall(r'-?\d+', eq)))
                return numbers[0], numbers[1], numbers[2]

            if st.button("Solve Equations"):
                try:
                    a1, b1, c1 = parse_eq(eq1)
                    a2, b2, c2 = parse_eq(eq2)
                    det = a1*b2 - a2*b1
                    if det != 0:
                        x = (c1*b2 - c2*b1)/det
                        y = (a1*c2 - a2*c1)/det
                        st.success(f"Solution: x = {x}, y = {y}")

                        # Graph
                        x_vals = np.linspace(-10, 10, 400)
                        y1 = (c1 - a1*x_vals) / b1
                        y2 = (c2 - a2*x_vals) / b2
                        fig, ax = plt.subplots()
                        ax.plot(x_vals, y1, label="Equation 1")
                        ax.plot(x_vals, y2, label="Equation 2")
                        ax.scatter(x, y, color="red", s=100, label="Solution")
                        ax.grid(True)
                        ax.legend()
                        st.pyplot(fig)
                    else:
                        st.error("No unique solution exists!")
                except Exception as e:
                    st.error("Error parsing equations. Make sure format is correct: `ax + by = c`")

# -------------------------
# TEACHER SECTION
# -------------------------
elif section == "Teacher Section":
    st.header("Teacher AI Assistant & GitHub Publisher")
    st.write("Generate or modify math lesson code and push to GitHub.")

    api_key = st.text_input("OpenAI API Key", type="password")
    github_token = st.text_input("GitHub Token", type="password")
    repo_name = st.text_input("GitHub Repo (username/repo)")
    topic = st.text_input("Topic Name to Add/Edit")
    edit_existing = st.checkbox("Edit Existing Topic?")

    if st.button("Generate/Update Topic Code") and api_key:
        openai.api_key = api_key
        if edit_existing:
            prompt = f"""
You are an AI assistant. Update the existing Streamlit code for the math topic '{topic}'.
Keep the interactive features, improve explanations, examples, or visualization as needed.
Return the Python code as plain text.
"""
        else:
            prompt = f"""
You are an AI assistant. Create a new Streamlit Python code for a math topic called '{topic}'.
Include header, interactive explanation, example input/output, and optional visualization.
Return only Python code as plain text.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

        topic_code = response.choices[0].message.content
        st.subheader("Generated Topic Code")
        st.code(topic_code, language="python")

        # Save temporarily
        os.makedirs("topics", exist_ok=True)
        file_path = f"topics/{topic.replace(' ', '_')}.py"
        with open(file_path, "w") as f:
            f.write(topic_code)
        st.success("Topic code generated successfully!")

    if st.button("Push to GitHub Repo") and github_token:
        try:
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            file_name = f"topics/{topic.replace(' ', '_')}.py"
            with open(f"topics/{topic.replace(' ', '_')}.py", "r") as f:
                content = f.read()
            # Create or update file
            try:
                existing_file = repo.get_contents(file_name)
                repo.update_file(existing_file.path, f"Update topic {topic}", content, existing_file.sha)
                st.success(f"Updated existing topic '{topic}' in GitHub repo!")
            except:
                repo.create_file(file_name, f"Add new topic {topic}", content)
                st.success(f"Added new topic '{topic}' to GitHub repo!")
        except Exception as e:
            st.error(f"Error pushing to GitHub: {e}")
