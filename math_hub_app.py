import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import glob
import json
import openai
import streamlit.components.v1 as components
from github import Github

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
os.makedirs("groups", exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state:
    st.session_state.teacher_name = ""
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False
if "special_answer_verified" not in st.session_state:
    st.session_state.special_answer_verified = False

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
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY

EDITOR_PASSWORD = "aceluffy"  # Editor login
SPECIAL_QUESTION = "Who do i love?"  # Private games question
SPECIAL_ANSWER = "riya"                  # Answer to access games

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
    dynamic_topics = [os.path.basename(f).replace(".py", "").replace("_"," ") for f in glob.glob("topics/*.py")]
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    # -------------------------
    # LCM & GCD Visualizer
    # -------------------------
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)
        gcd = math.gcd(a,b)
        lcm = a*b//gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")

        factors_a = [i for i in range(1,a+1) if a%i==0]
        factors_b = [i for i in range(1,b+1) if b%i==0]
        multiples_a = [a*i for i in range(1,10)]
        multiples_b = [b*i for i in range(1,10)]

        fig, ax = plt.subplots()
        # Color-blind friendly palette
        colors = {"factors_a":"#E69F00","factors_b":"#56B4E9","multiples_a":"#009E73","multiples_b":"#D55E00"}
        ax.scatter(factors_a,[1]*len(factors_a), marker="s", color=colors["factors_a"], label="Factors A")
        ax.scatter(factors_b,[2]*len(factors_b), marker="s", color=colors["factors_b"], label="Factors B")
        ax.scatter(multiples_a,[3]*len(multiples_a), marker="o", color=colors["multiples_a"], label="Multiples A")
        ax.scatter(multiples_b,[4]*len(multiples_b), marker="o", color=colors["multiples_b"], label="Multiples B")
        ax.scatter(lcm,2.5,color="#009E73", s=120, label="LCM")
        ax.scatter(gcd,0.5,color="#E69F00", s=120, label="GCD")
        for x in factors_a: ax.text(x,1.05,str(x),ha="center")
        for x in factors_b: ax.text(x,2.05,str(x),ha="center")
        for x in multiples_a: ax.text(x,3.05,str(x),ha="center")
        for x in multiples_b: ax.text(x,4.05,str(x),ha="center")
        ax.set_yticks([0.5,1,2,2.5,3,4])
        ax.set_yticklabels(["GCD","Factors A","Factors B","LCM","Multiples A","Multiples B"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # Prime Factors
    # -------------------------
    elif topic=="Prime Factors":
        st.header("Prime Factorization")
        n = st.number_input("Enter Number",2,1000,24)
        if st.button("Find Prime Factors"):
            factors=[]
            temp=n
            for i in range(2,temp+1):
                while temp%i==0:
                    factors.append(i)
                    temp=temp//i
            st.write("Prime factors:", factors)

    # -------------------------
    # Ratios
    # -------------------------
    elif topic=="Ratios":
        st.header("Ratio Simplifier")
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)
        if st.button("Simplify Ratio"):
            g = math.gcd(a,b)
            st.write("Simplified Ratio:", f"{a//g}:{b//g}")

    # -------------------------
    # Simultaneous Equations Solver
    # -------------------------
    elif topic=="Simultaneous Equations":
        st.header("2x2 Simultaneous Equations Solver")
        a1 = st.number_input("a1", -50, 50, 2)
        b1 = st.number_input("b1", -50, 50, 3)
        c1 = st.number_input("c1", -100, 100, 11)
        a2 = st.number_input("a2", -50, 50, 1)
        b2 = st.number_input("b2", -50, 50, -1)
        c2 = st.number_input("c2", -100, 100, 1)

        if st.button("Solve and Animate"):
            det = a1*b2 - a2*b1
            if det==0:
                st.error("No unique solution exists")
            else:
                x_sol = (c1*b2 - c2*b1)/det
                y_sol = (a1*c2 - a2*c1)/det
                st.success(f"Solution: x = {x_sol}, y = {y_sol}")

                x_vals = np.linspace(-20,20,400)
                y1_vals = (c1 - a1*x_vals)/b1
                y2_vals = (c2 - a2*x_vals)/b2
                fig,ax=plt.subplots(figsize=(7,6))
                ax.plot(x_vals,y1_vals, label=f"{a1}x + {b1}y = {c1}", color="#0072B2")
                ax.plot(x_vals,y2_vals, label=f"{a2}x + {b2}y = {c2}", color="#D55E00")
                ax.scatter(x_sol,y_sol,color="red",s=100,label="Intersection")
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

    # -------------------------
    # Learner Group Chat
    # -------------------------
    st.subheader("Groups")
    group_name = st.text_input("Enter your group name to join/create")
    learner_name = st.text_input("Your Name")
    if group_name and learner_name:
        chat_file = f"groups/group_{group_name}.json"
        if os.path.exists(chat_file):
            with open(chat_file) as f:
                chat_history = json.load(f)
        else:
            chat_history=[]
        new_message = st.text_input("Type your message")
        if st.button("Send to Group"):
            if new_message.strip():
                chat_history.append({"sender":learner_name,"message":new_message})
                with open(chat_file,"w") as f:
                    json.dump(chat_history,f)
                st.experimental_rerun()
        st.write(f"Messages in {group_name}:")
        for msg in chat_history:
            st.write(f"{msg['sender']}: {msg['message']}")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type=="Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password",type="password")
    teacher_number = st.text_input("Your Number Tag")
    if st.button("Register/Login"):
        if username not in teacher_data:
            teacher_data[username]=password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
        elif teacher_data[username]==password:
            st.success("Login successful")
            st.session_state.teacher_logged_in=True
            st.session_state.teacher_name=username
        else:
            st.error("Wrong password")

    if st.session_state.teacher_logged_in:
        st.subheader("Submit Topic Description")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Description"):
            submission = {"teacher":st.session_state.teacher_name,
                          "topic_number":teacher_number,
                          "topic_name":topic_name,
                          "topic_description":topic_description}
            filename=f"submissions/{topic_name.replace(' ','_')}.json"
            with open(filename,"w") as f:
                json.dump(submission,f)
            st.success("Submitted for editor approval!")

        # -------- Teacher Group Chat --------
        st.subheader("Group Chats with Learners")
        groups_list = [f.replace(".json","").replace("group_","") for f in glob.glob("groups/group_*.json")]
        selected_group = st.selectbox("Select a group", ["--Select Group--"] + groups_list)
        if selected_group!="--Select Group--":
            chat_file = f"groups/group_{selected_group}.json"
            if os.path.exists(chat_file):
                with open(chat_file) as f:
                    chat_history = json.load(f)
            else:
                chat_history=[]
            st.write(f"Group Chat: {selected_group}")
            for msg in chat_history:
                st.write(f"{msg['sender']}: {msg['message']}")
            teacher_message = st.text_input("Your reply to the group")
            if st.button("Send to Group"):
                if teacher_message.strip():
                    chat_history.append({"sender":f"Teacher {st.session_state.teacher_name}","message":teacher_message})
                    with open(chat_file,"w") as f:
                        json.dump(chat_history,f)
                    st.success("Message sent!")
                    st.experimental_rerun()
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

        # Load all teacher submissions
        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data = json.load(f)
            st.write("Teacher:", data["teacher"])
            st.write("Topic Name:", data["topic_name"])
            st.write("Description:", data["topic_description"])
            st.code(data.get("topic_code",""))

            # Button to generate Python code using OpenAI
            if st.button(f"Generate Code for {data['topic_name']}", key=file+"_generate"):
                if OPENAI_API_KEY:
                    prompt = f"Generate a Python code snippet for this topic:\n{data['topic_description']}"
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        max_tokens=500
                    )
                    generated_code = response.choices[0].text.strip()
                    data["topic_code"] = generated_code
                    with open(file,"w") as f:
                        json.dump(data,f)
                    st.code(generated_code)
                    st.success("Code generated successfully!")
                else:
                    st.error("OpenAI API key missing!")

            # Button to approve & push topic to GitHub
            if st.button(f"Approve & Push {data['topic_name']}", key=file+"_push"):
                if not repo_name:
                    st.error("Enter your GitHub repo in the format username/repo")
                else:
                    try:
                        g = Github(GITHUB_TOKEN)
                        repo = g.get_repo(repo_name)
                        filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                        if os.path.exists(filename):
                            repo.update_file(filename, f"Update topic {data['topic_name']}", data["topic_code"], repo.get_contents(filename).sha)
                        else:
                            repo.create_file(filename, f"Add topic {data['topic_name']}", data["topic_code"])
                        os.rename(file, f"approved/{os.path.basename(file)}")
                        st.success("Topic approved and pushed to GitHub!")
                    except Exception as e:
                        st.error(f"GitHub Error: {e}")

        # -------------------------
        # PRIVATE GAMES SECTION
        # -------------------------
        st.subheader("Private Mini-Games")
        if not st.session_state.special_answer_verified:
            st.info("Answer the special question to access games")
            answer = st.text_input(SPECIAL_QUESTION)
            if st.button("Submit Answer"):
                if answer.strip() == SPECIAL_ANSWER:
                    st.session_state.special_answer_verified = True
                    st.success("Access granted!")
                else:
                    st.error("Wrong answer, try again")
        else:
            st.success("You can access your private games below!")

            # Example: GTA-style mini-game (placeholder link)
            gta_url = "https://www.hero-wars.com/?hl=en"  # Replace with your GTA-like game
            st.markdown(f"[Play GTA-style Game]({gta_url})")
            components.iframe(gta_url, width=1000, height=600)

            # Add more games here
            st.markdown("Other mini-games coming soon!")

    else:
        st.info("Enter editor password to access this section.")
