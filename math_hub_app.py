import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import glob
import json
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
if "color_blind" not in st.session_state:
    st.session_state.color_blind = False
if "games_access" not in st.session_state:
    st.session_state.games_access = False

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
# SECRETS & CONFIG
# -------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

EDITOR_PASSWORD = "aceluffy"
SPECIAL_QUESTION = "What is the secret word for games?"
SPECIAL_ANSWER = "mathhub123"

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    
    st.checkbox("Enable Color-Blind Mode", key="color_blind")
    
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py", "").replace("_", " ") for f in glob.glob("topics/*.py")]
    
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    # -- LCM & GCD --
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)
        if st.button("Calculate"):
            gcd = math.gcd(a, b)
            lcm = a * b // gcd
            st.success(f"GCD = {gcd}")
            st.success(f"LCM = {lcm}")
            multiples_a = [a*i for i in range(1,10)]
            multiples_b = [b*i for i in range(1,10)]
            factors_a = [i for i in range(1,a+1) if a%i==0]
            factors_b = [i for i in range(1,b+1) if b%i==0]

            # Color-blind mode
            if st.session_state.color_blind:
                factor_a_color, factor_b_color = "black", "gray"
                mult_a_color, mult_b_color = "purple", "cyan"
            else:
                factor_a_color, factor_b_color = "orange", "blue"
                mult_a_color, mult_b_color = "green", "red"

            fig, ax = plt.subplots()
            ax.scatter(factors_a,[1]*len(factors_a), marker="s", color=factor_a_color, label="Factors A")
            ax.scatter(factors_b,[2]*len(factors_b), marker="s", color=factor_b_color, label="Factors B")
            ax.scatter(multiples_a,[3]*len(multiples_a), marker="o", color=mult_a_color, label="Multiples A")
            ax.scatter(multiples_b,[4]*len(multiples_b), marker="o", color=mult_b_color, label="Multiples B")
            ax.scatter(lcm,2.5, color=mult_a_color, s=120, label="LCM")
            ax.scatter(gcd,0.5, color=factor_a_color, s=120, label="GCD")
            for x in factors_a: ax.text(x,1.05,str(x),ha="center")
            for x in factors_b: ax.text(x,2.05,str(x),ha="center")
            for x in multiples_a: ax.text(x,3.05,str(x),ha="center")
            for x in multiples_b: ax.text(x,4.05,str(x),ha="center")
            ax.set_yticks([0.5,1,2,3,4,2.5])
            ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","Multiples B","LCM"])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)

    # -- Prime Factors --
    elif topic == "Prime Factors":
        st.header("Prime Factorization")
        n = st.number_input("Enter Number",2,100,24)
        if st.button("Find Prime Factors"):
            factors=[]
            temp=n
            d=2
            while temp>1:
                while temp%d==0:
                    factors.append(d)
                    temp//=d
                d+=1
            st.write("Prime factors:", factors)

    # -- Ratios --
    elif topic=="Ratios":
        st.header("Ratios")
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)
        if st.button("Simplify Ratio"):
            g = math.gcd(a,b)
            st.write(f"Simplified Ratio: {a//g}:{b//g}")

    # -- Simultaneous Equations --
    elif topic=="Simultaneous Equations":
        st.header("Animated Simultaneous Equations Solver")
        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)

        if st.button("Animate Solution"):
            det = a1*b2 - a2*b1
            if det==0:
                st.error("No unique solution exists")
            else:
                x_sol = (c1*b2 - c2*b1)/det
                y_sol = (a1*c2 - a2*c1)/det
                x_vals = np.linspace(-10,10,400)
                y1_vals = (c1-a1*x_vals)/b1
                y2_vals = (c2-a2*x_vals)/b2

                fig,ax=plt.subplots(figsize=(8,6))
                line1,line2,point = ax.plot([],[],label=f"{a1}x + {b1}y = {c1}")[0],ax.plot([],[],label=f"{a2}x + {b2}y = {c2}")[0],ax.plot([],[],'ro',markersize=10)[0]
                ax.set_xlim(-10,10)
                ax.set_ylim(-10,10)
                ax.grid(True)
                ax.legend()
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.set_title("Lines moving toward intersection")

                def animate(i):
                    line1.set_data(x_vals[:i],y1_vals[:i])
                    line2.set_data(x_vals[:i],y2_vals[:i])
                    if i>0:
                        point.set_data([x_sol],[y_sol])
                    return line1,line2,point

                ani = FuncAnimation(fig, animate, frames=len(x_vals), interval=20, blit=True)
                st.pyplot(fig)
                st.success(f"Solution: x={x_sol}, y={y_sol}")

    # -- Learner-Teacher Chat --
    st.subheader("Chat with Teacher")
    learner_name = st.text_input("Your Name")
    teacher_number = st.text_input("Teacher Number")
    chat_file = f"messages/{teacher_number}.json"
    if os.path.exists(chat_file):
        with open(chat_file) as f:
            chat_history = json.load(f)
    else:
        chat_history=[]
    new_message = st.text_input("Type your message")
    if st.button("Send"):
        if learner_name.strip() and new_message.strip():
            chat_history.append({"sender":learner_name,"message":new_message})
            with open(chat_file,"w") as f:
                json.dump(chat_history,f)
            st.experimental_rerun()
    st.write("Messages:")
    for msg in chat_history:
        st.write(f"{msg['sender']}: {msg['message']}")

    # -- Learner Groups --
    st.subheader("Learner Groups")
    group_action = st.selectbox("Group Actions", ["Create Group","Join Group","My Groups"])
    if group_action=="Create Group":
        group_name = st.text_input("Group Name")
        if st.button("Create Group"):
            group_file = f"groups/{group_name}.json"
            if os.path.exists(group_file):
                st.warning("Group exists!")
            else:
                json.dump({"group_name":group_name,"members":[learner_name],"chat_history":[]},open(group_file,"w"))
                st.success(f"Group '{group_name}' created!")
    elif group_action=="Join Group":
        available_groups = [f.replace(".json","") for f in os.listdir("groups")]
        selected_group = st.selectbox("Available Groups", available_groups)
        if st.button("Join Group"):
            group_file = f"groups/{selected_group}.json"
            with open(group_file) as f:
                data=json.load(f)
            if learner_name not in data["members"]:
                data["members"].append(learner_name)
                with open(group_file,"w") as f:
                    json.dump(data,f)
                st.success(f"You joined '{selected_group}'!")
            else:
                st.info("Already in this group.")

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type=="Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_number = st.text_input("Your Number Tag")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered successfully")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username]==password:
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
            submission = {"teacher":st.session_state.teacher_name,"topic_number":teacher_number,"topic_name":topic_name,"topic_description":topic_description}
            filename = f"submissions/{topic_name.replace(' ','_')}.json"
            with open(filename,"w") as f:
                json.dump(submission,f)
            st.success("Topic submitted for editor approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type=="Editor":
    st.header("Editor Dashboard")
    editor_pass_input = st.text_input("Enter Editor Password", type="password")
    if editor_pass_input==EDITOR_PASSWORD:
        st.session_state.editor_logged_in=True

    if st.session_state.editor_logged_in:
        st.subheader("Approve Topics & Generate Python Code")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file) as f:
                data=json.load(f)
            st.write("Teacher:",data["teacher"])
            st.write("Topic Name:",data["topic_name"])
            st.write("Description:",data["topic_description"])
            st.code(data.get("topic_code",""))

            if st.button(f"Generate Code for {data['topic_name']}",key=file):
                prompt = f"Generate a Python code snippet for the following topic:\n{data['topic_description']}"
                response = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=500)
                generated_code = response.choices[0].text.strip()
                data["topic_code"] = generated_code
                with open(file,"w") as f:
                    json.dump(data,f)
                st.code(generated_code)
                st.success("Code generated!")

            if st.button(f"Approve & Push {data['topic_name']}",key=file+"_push"):
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    if os.path.exists(filename):
                        repo.update_file(filename,f"Update topic {data['topic_name']}",data["topic_code"],repo.get_contents(filename).sha)
                    else:
                        repo.create_file(filename,f"Add topic {data['topic_name']}",data["topic_code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success("Topic approved and pushed to GitHub!")
                except Exception as e:
                    st.error(e)

        # -- Mini Games (Private) --
        st.subheader("Private Mini Games Access")
        answer = st.text_input("Answer the special question to access games:")
        st.write(f"Question: {SPECIAL_QUESTION}")
        if answer == SPECIAL_ANSWER:
            st.session_state.games_access=True
        if st.session_state.games_access:
            st.success("Access granted!")
            st.markdown("[Play GTA San Andreas Mini Game](#)")
            # Add more mini games here
        else:
            st.info("Enter correct answer to access mini games.")
    else:
        st.info("Enter editor password to access this section.")
