import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
import smtplib
from email.message import EmailMessage
from github import Github
import openai
import streamlit.components.v1 as components

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊", layout="centered")
st.title("📊 Interactive Math Hub")

# -------------------------
# CREATE REQUIRED FOLDERS
# -------------------------
os.makedirs("topics", exist_ok=True)
os.makedirs("submissions", exist_ok=True)
os.makedirs("approved", exist_ok=True)
os.makedirs("messages", exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False

# -------------------------
# LOAD TEACHERS
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
EMAIL_SENDER = st.secrets.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY

EDITOR_PASSWORD = "aceluffy"  # Editor login password

# -------------------------
# SPECIAL QUESTION FOR GAMES ACCESS
# -------------------------
# <<< SET YOUR QUESTION AND ANSWER HERE >>>
SPECIAL_QUESTION = "Who do i like?"
SPECIAL_ANSWER = "my sis's"  # <-- Replace this with your secret answer

# -------------------------
# COLOR-BLIND MODE
# -------------------------
color_blind_mode = st.sidebar.checkbox("Color-Blind Friendly Mode")

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py", "").replace("_", " ") for f in glob.glob("topics/*.py")]
    
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)
    
    # -------------------------
    # LCM & GCD
    # -------------------------
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)
        gcd = math.gcd(a, b)
        lcm = a * b // gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")
        factors_a = [i for i in range(1, a+1) if a % i == 0]
        factors_b = [i for i in range(1, b+1) if b % i == 0]
        multiples_a = [a * i for i in range(1, 10)]
        multiples_b = [b * i for i in range(1, 10)]

        fig, ax = plt.subplots()
        y_positions = [1, 2, 3, 4]
        c1, c2, c3, c4 = "orange", "blue", "green", "red"
        if color_blind_mode:
            c1, c2, c3, c4 = "#E69F00", "#56B4E9", "#009E73", "#D55E00"  # color-blind friendly palette
        ax.scatter(factors_a, [y_positions[0]]*len(factors_a), marker="s", color=c1, label="Factors A")
        ax.scatter(factors_b, [y_positions[1]]*len(factors_b), marker="s", color=c2, label="Factors B")
        ax.scatter(multiples_a, [y_positions[2]]*len(multiples_a), marker="o", color=c3, label="Multiples A")
        ax.scatter(multiples_b, [y_positions[3]]*len(multiples_b), marker="o", color=c4, label="Multiples B")
        ax.scatter(lcm, 2.5, color=c3, s=120, label="LCM")
        ax.scatter(gcd, 0.5, color=c1, s=120, label="GCD")
        for x in factors_a: ax.text(x, 1.05, str(x), ha="center")
        for x in factors_b: ax.text(x, 2.05, str(x), ha="center")
        for x in multiples_a: ax.text(x, 3.05, str(x), ha="center")
        for x in multiples_b: ax.text(x, 4.05, str(x), ha="center")
        ax.set_yticks([0.5, 1, 2, 3, 4, 2.5])
        ax.set_yticklabels(["GCD", "Factors A", "Factors B", "Multiples A", "Multiples B", "LCM"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # Ratios
    # -------------------------
    elif topic == "Ratios":
        st.header("Ratios")
        a = st.number_input("Value A", 1, 100, 4)
        b = st.number_input("Value B", 1, 100, 6)
        st.write(f"The ratio A:B is {a}:{b}")

    # -------------------------
    # Prime Factors
    # -------------------------
    elif topic == "Prime Factors":
        st.header("Prime Factors")
        n = st.number_input("Enter a number", 2, 100, 12)
        factors = []
        temp = n
        for i in range(2, temp+1):
            while temp % i == 0:
                factors.append(i)
                temp = temp // i
        st.write("Prime factors:", factors)

    # -------------------------
    # Simultaneous Equations
    # -------------------------
    elif topic == "Simultaneous Equations":
        st.header("Interactive Simultaneous Equation Solver")
        st.write("Enter your 2x2 equations:")

        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)

        if st.button("Solve & Animate"):
            det = a1*b2 - a2*b1
            if det == 0:
                st.error("No unique solution (lines may be parallel)")
            else:
                x_sol = (c1*b2 - c2*b1)/det
                y_sol = (a1*c2 - a2*c1)/det
                st.success(f"Solution: x = {x_sol}, y = {y_sol}")

                x_vals = np.linspace(-10, 10, 400)
                y1_vals = (c1 - a1*x_vals)/b1
                y2_vals = (c2 - a2*x_vals)/b2

                fig, ax = plt.subplots(figsize=(8,6))
                line1, = ax.plot([], [], label=f"{a1}x + {b1}y = {c1}")
                line2, = ax.plot([], [], label=f"{a2}x + {b2}y = {c2}")
                point, = ax.plot([], [], 'ro', markersize=10)

                ax.set_xlim(-10,10)
                ax.set_ylim(-10,10)
                ax.grid(True)
                ax.legend()
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.set_title("Lines moving toward intersection")

                for i in range(len(x_vals)):
                    line1.set_data(x_vals[:i], y1_vals[:i])
                    line2.set_data(x_vals[:i], y2_vals[:i])
                    point.set_data(x_sol, y_sol)
                    st.pyplot(fig)

    # -------------------------
    # Learner-Teacher Chat
    # -------------------------
    st.subheader("Chat with Teacher")
    learner_name = st.text_input("Your Name")
    teacher_number = st.text_input("Teacher Number")
    chat_file = f"messages/{teacher_number}.json"
    if os.path.exists(chat_file):
        with open(chat_file) as f:
            chat_history = json.load(f)
    else:
        chat_history = []
    new_message = st.text_input("Type your message")
    if st.button("Send"):
        if learner_name.strip() and new_message.strip():
            chat_history.append({"sender": learner_name, "message": new_message})
            with open(chat_file, "w") as f:
                json.dump(chat_history, f)
            st.experimental_rerun()
    st.write("Messages:")
    for msg in chat_history:
        st.write(f"{msg['sender']}: {msg['message']}")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_number = st.text_input("Your Number Tag (for chat)")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE, "w") as f:
                json.dump(teacher_data, f)
            st.success("Registered successfully")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username] == password:
            st.success("Login successful")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        else:
            st.error("Wrong password")

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic Description")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Description"):
            submission = {
                "teacher": st.session_state.teacher_name,
                "topic_number": teacher_number,
                "topic_name": topic_name,
                "topic_description": topic_description
            }
            filename = f"{topic_name.replace(' ', '_')}.json"
            with open(f"submissions/{filename}", "w") as f:
                json.dump(submission, f)
            st.success("Topic description submitted for editor approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard")
    editor_pass_input = st.text_input("Enter Editor Password", type="password")
    if editor_pass_input == EDITOR_PASSWORD:
        st.session_state.editor_logged_in = True

    if st.session_state.editor_logged_in:
        st.subheader("Approve Topics & Generate Python Code")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.write("Teacher:", data["teacher"])
            st.write("Topic Name:", data["topic_name"])
            st.write("Description:", data["topic_description"])
            st.code(data.get("topic_code", ""))

            if st.button(f"Generate Code for {data['topic_name']}", key=file):
                prompt = f"Generate a Python code snippet for the following topic:\n{data['topic_description']}"
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt,
                    max_tokens=500
                )
                generated_code = response.choices[0].text.strip()
                data["topic_code"] = generated_code
                with open(file, "w") as f:
                    json.dump(data, f)
                st.code(generated_code)
                st.success("Code generated!")

            if st.button(f"Approve & Push {data['topic_name']}", key=file+"_push"):
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ', '_')}.py"
                    if os.path.exists(filename):
                        repo.update_file(filename, f"Update topic {data['topic_name']}", data["topic_code"], repo.get_contents(filename).sha)
                    else:
                        repo.create_file(filename, f"Add topic {data['topic_name']}", data["topic_code"])
                    os.rename(file, f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)

        # -------------------------
        # PRIVATE GAME ACCESS
        # -------------------------
        st.subheader("Play Your Games (Private Access)")
        user_answer = st.text_input(SPECIAL_QUESTION)
        if user_answer == SPECIAL_ANSWER:
            st.success("Access granted! You can now play the games.")
            game_option = st.selectbox(
                "Choose a Game to Play",
                ["Hero Wars 3D", "Mini GTA Sandbox"]
            )

            if game_option == "Hero Wars 3D":
                game_url = "https://www.hero-wars.com/?hl=en"
                st.markdown(f"[Click to play Hero Wars 3D]({game_url})")
                components.iframe(game_url, width=1000, height=600)

            elif game_option == "Mini GTA Sandbox":
                st.markdown("**Mini GTA Sandbox** – 2D top-down open-world game demo")
                st.write("Use arrow keys to move your character. Drive cars and explore the map!")
                gta_demo_url = "https://yourhostedminigta.com"  # Hosted HTML5/JS version
                components.iframe(gta_demo_url, width=1000, height=600)
        else:
            st.info("You must answer the special question correctly to access the games.")
