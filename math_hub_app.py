import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
from email.message import EmailMessage
import smtplib
from github import Github
import openai

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
os.makedirs("chats", exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "learner_name" not in st.session_state:
    st.session_state.learner_name = ""

# -------------------------
# PASSWORD FILE
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    st.write("Enter your name:")
    learner_name = st.text_input("Your Name")
    if learner_name:
        st.session_state.learner_name = learner_name

    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py","").replace("_"," ") for f in glob.glob("topics/*.py")]

    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    # ===== LCM & GCD =====
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
        multiples_a = [a*i for i in range(1,10)]
        multiples_b = [b*i for i in range(1,10)]

        st.write("Factors A:", factors_a)
        st.write("Factors B:", factors_b)
        st.write("Multiples A:", multiples_a)
        st.write("Multiples B:", multiples_b)

        fig, ax = plt.subplots()
        y_positions = [1,2,3,4]
        ax.scatter(factors_a,[y_positions[0]]*len(factors_a), marker="s", color="orange", label="Factors A")
        ax.scatter(factors_b,[y_positions[1]]*len(factors_b), marker="s", color="blue", label="Factors B")
        ax.scatter(multiples_a,[y_positions[2]]*len(multiples_a), marker="o", color="green", label="Multiples A")
        ax.scatter(multiples_b,[y_positions[3]]*len(multiples_b), marker="o", color="red", label="Multiples B")
        ax.scatter(lcm, 2.5, color="green", s=120, label="LCM")
        ax.scatter(gcd, 0.5, color="orange", s=120, label="GCD")
        ax.set_yticks([0.5,1,2,3,4,2.5])
        ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # ===== Dynamic Topics =====
    elif topic in dynamic_topics:
        file_path = f"topics/{topic.replace(' ','_')}.py"
        with open(file_path) as f:
            exec(f.read())

    # ===== Learner-Teacher Chat =====
    st.subheader("Chat with Teachers")
    chat_file = f"chats/{st.session_state.learner_name}.json"
    if os.path.exists(chat_file):
        with open(chat_file) as f:
            chat_data = json.load(f)
        for msg in chat_data:
            st.write(f"**{msg['sender']}:** {msg['message']}")
    else:
        chat_data = []

    msg_input = st.text_input("Send a message to teacher")
    if st.button("Send Message"):
        if msg_input:
            chat_data.append({"sender": st.session_state.learner_name, "message": msg_input})
            with open(chat_file, "w") as f:
                json.dump(chat_data,f)
            st.experimental_rerun()

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered successfully")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
        elif teacher_data[username]==password:
            st.success("Login successful")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
        else:
            st.error("Wrong password")

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Description")
        topic_code = st.text_area("Python Code")

        if st.button("Generate Python Code from Description"):
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            prompt = f"Create Python code for this topic: {topic_description}"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300
            )
            topic_code = response.choices[0].text.strip()
            st.code(topic_code)

        if st.button("Submit Topic"):
            submission = {
                "teacher": st.session_state.teacher_name,
                "topic_name": topic_name,
                "topic_description": topic_description,
                "topic_code": topic_code
            }
            filename = topic_name.replace(" ","_") + ".json"
            with open(f"submissions/{filename}", "w") as f:
                json.dump(submission,f)
            st.success("Topic submitted for approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Dashboard (Private Features)")
    editor_password_input = st.text_input("Enter Special Editor Password", type="password")
    if editor_password_input == "YourSuperSecret123":  # Set your editor password
        st.success("Access granted to private editor features!")

        st.subheader("GitHub Approval")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")

        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.subheader(data["topic_name"])
            st.write("Teacher:", data["teacher"])
            st.write("Description:", data["topic_description"])
            st.code(data["topic_code"])
            if st.button(f"Approve {data['topic_name']}", key=file):
                try:
                    g = Github(st.secrets["GITHUB_TOKEN"])
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    repo.create_file(filename, "Add topic", data["topic_code"])
                    os.rename(file, f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)

        # ===== Private 3D Mini-Game =====
        st.subheader("Private 3D Mini-Game")
        st.components.v1.html("""
        <canvas id="canvas"></canvas>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas')});
        renderer.setSize(400, 400);
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({color: 0x00ff00, wireframe:true});
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        camera.position.z = 5;
        function animate() {
            requestAnimationFrame(animate);
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
        </script>
        """, height=450)
    else:
        st.warning("Enter the correct password to access your private editor features.")
