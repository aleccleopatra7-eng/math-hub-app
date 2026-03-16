import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
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
if "teacher_logged_in" not in st.session_state: st.session_state.teacher_logged_in = False
if "teacher_name" not in st.session_state: st.session_state.teacher_name = ""
if "editor_logged_in" not in st.session_state: st.session_state.editor_logged_in = False
if "special_answer_verified" not in st.session_state: st.session_state.special_answer_verified = False

# -------------------------
# LOAD TEACHERS
# -------------------------
PASSWORD_FILE = "teachers.json"
if os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE,"r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY
EDITOR_PASSWORD = "aceluffy"
SPECIAL_QUESTION = "who is my chizi?"
SPECIAL_ANSWER = "riya"

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    
    # Topics selection
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py","").replace("_"," ") for f in glob.glob("topics/*.py")]
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)
    
    # -------------------------
    # LCM & GCD
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
        fig,ax = plt.subplots()
        ax.scatter(factors_a,[1]*len(factors_a), marker="s", color="orange", label="Factors A")
        ax.scatter(factors_b,[2]*len(factors_b), marker="s", color="blue", label="Factors B")
        ax.scatter(multiples_a,[3]*len(multiples_a), marker="o", color="green", label="Multiples A")
        ax.scatter(multiples_b,[4]*len(multiples_b), marker="o", color="red", label="Multiples B")
        ax.scatter(lcm,3.5,color="green",s=120,label="LCM")
        ax.scatter(gcd,0.5,color="orange",s=120,label="GCD")
        for x in factors_a: ax.text(x,1.05,str(x),ha="center")
        for x in factors_b: ax.text(x,2.05,str(x),ha="center")
        for x in multiples_a: ax.text(x,3.05,str(x),ha="center")
        for x in multiples_b: ax.text(x,4.05,str(x),ha="center")
        ax.set_yticks([0.5,1,2,3,3.5,4])
        ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","LCM","Multiples B"])
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # Ratios
    # -------------------------
    elif topic == "Ratios":
        st.header("Ratios")
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)
        st.write(f"The ratio A:B is {a}:{b}")

    # -------------------------
    # Prime Factors
    # -------------------------
    elif topic == "Prime Factors":
        st.header("Prime Factors")
        n = st.number_input("Enter a number",2,100,12)
        factors=[]
        temp=n
        for i in range(2,temp+1):
            while temp%i==0:
                factors.append(i)
                temp//=i
        st.write("Prime factors:", factors)

    # -------------------------
    # Simultaneous Equations
    # -------------------------
    elif topic == "Simultaneous Equations":
        st.header("Simultaneous Equation Solver")
        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)
        if st.button("Solve Equations"):
            det = a1*b2 - a2*b1
            if det !=0:
                x = (c1*b2 - c2*b1)/det
                y = (a1*c2 - a2*c1)/det
                st.success(f"Solution: x = {x}, y = {y}")
                # Plot lines
                x_vals = np.linspace(-10,10,400)
                y1_vals = (c1 - a1*x_vals)/b1
                y2_vals = (c2 - a2*x_vals)/b2
                fig,ax = plt.subplots()
                ax.plot(x_vals,y1_vals,label=f"{a1}x + {b1}y = {c1}")
                ax.plot(x_vals,y2_vals,label=f"{a2}x + {b2}y = {c2}")
                ax.scatter(x,y,color="red",s=120)
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)
            else:
                st.error("No unique solution (lines may be parallel)")

    # -------------------------
    # Learner-Teacher / Group Chat
    # -------------------------
    st.subheader("Chat with Teacher / Group")
    learner_name = st.text_input("Your Name")
    teacher_code = st.text_input("Teacher Code")
    group_name = st.text_input("Group Name (optional)")
    chat_file = f"groups/{teacher_code}_{group_name}.json" if group_name else f"messages/{teacher_code}.json"
    
    # Safe loading and auto-join
    if os.path.exists(chat_file):
        with open(chat_file,"r") as f:
            chat_history = json.load(f)
    else:
        chat_history = {"members":[],"messages":[]}
        with open(chat_file,"w") as f:
            json.dump(chat_history,f)
    
    if learner_name.strip() and learner_name not in chat_history["members"]:
        chat_history["members"].append(learner_name)
        with open(chat_file,"w") as f:
            json.dump(chat_history,f)
    
    # Display chat messages
    st.write("Messages:")
    for msg in chat_history.get("messages",[]):
        st.write(f"{msg['sender']}: {msg['message']}")
    
    # Send message
    new_msg = st.text_input("Type your message")
    if st.button("Send Message"):
        if learner_name.strip() and new_msg.strip():
            chat_history["messages"].append({"sender": learner_name, "message": new_msg})
            with open(chat_file,"w") as f:
                json.dump(chat_history,f)
            st.experimental_rerun()

# =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_code = st.text_input("Your Teacher Code (used for groups & chat)")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open("teachers.json","w") as f:
                json.dump(teacher_data,f)
            st.success("Registered successfully!")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username]==password:
            st.success("Login successful!")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        else:
            st.error("Wrong password!")

    if st.session_state.teacher_logged_in:
        st.subheader("Create a Group")
        group_name = st.text_input("Group Name")
        if st.button("Create Group"):
            if group_name.strip() and teacher_code.strip():
                group_file = f"groups/{teacher_code}_{group_name}.json"
                if not os.path.exists(group_file):
                    with open(group_file,"w") as f:
                        json.dump({"teacher": username, "members": [], "messages":[]},f)
                    st.success(f"Group '{group_name}' created successfully with code '{teacher_code}'")
                else:
                    st.warning("Group already exists!")

        st.subheader("Group Chat")
        chat_group_name = st.text_input("Select Group for Chat")
        chat_file = f"groups/{teacher_code}_{chat_group_name}.json"
        if os.path.exists(chat_file):
            with open(chat_file,"r") as f:
                group_data = json.load(f)
        else:
            group_data = {"teacher": username, "members": [], "messages":[]}

        new_msg = st.text_input("Type your message to group")
        if st.button("Send to Group"):
            if new_msg.strip():
                group_data["messages"].append({"sender": username, "message": new_msg})
                with open(chat_file,"w") as f:
                    json.dump(group_data,f)
                st.experimental_rerun()

        st.write("Group Messages:")
        for msg in group_data.get("messages",[]):
            st.write(f"{msg['sender']}: {msg['message']}")

        st.subheader("Submit Topic Description")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Topic"):
            if topic_name.strip() and topic_description.strip():
                submission = {
                    "teacher": username,
                    "teacher_code": teacher_code,
                    "topic_name": topic_name,
                    "topic_description": topic_description
                }
                filename = f"submissions/{topic_name.replace(' ','_')}.json"
                with open(filename,"w") as f:
                    json.dump(submission,f)
                st.success("Topic submitted for editor approval!")
                
# =====================================================
# EDITOR SECTION (Fixed for reliable code generation)
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
            with open(file,"r") as f:
                data = json.load(f)

            st.write("Teacher:", data.get("teacher",""))
            st.write("Topic Name:", data.get("topic_name",""))
            st.write("Description:", data.get("topic_description",""))
            st.code(data.get("topic_code",""))

            # Unique keys for Streamlit buttons
            generate_key = f"generate_{data.get('topic_name','')}_{file}"
            push_key = f"push_{data.get('topic_name','')}_{file}"

            # -------------------------
            # Generate Python Code
            # -------------------------
            if st.button(f"Generate Code for {data.get('topic_name','')}", key=generate_key):
                if OPENAI_API_KEY:
                    if "topic_description" not in data or not data["topic_description"].strip():
                        st.error("Topic description is missing! Cannot generate code.")
                        continue
                    prompt = f"Generate a Python code snippet for this topic:\n{data['topic_description']}"
                    try:
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
                    except Exception as e:
                        st.error(f"OpenAI API Error: {e}")
                else:
                    st.error("OpenAI API key is missing!")

            # -------------------------
            # Approve & Push to GitHub
            # -------------------------
            if st.button(f"Approve & Push {data.get('topic_name','')}", key=push_key):
                if not repo_name.strip():
                    st.error("Enter GitHub repo as username/repo")
                    continue
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    if os.path.exists(filename):
                        # Update existing file
                        contents = repo.get_contents(filename)
                        repo.update_file(filename, f"Update topic {data['topic_name']}", data["topic_code"], contents.sha)
                    else:
                        # Create new file
                        repo.create_file(filename, f"Add topic {data['topic_name']}", data["topic_code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success(f"Topic '{data['topic_name']}' approved and pushed!")
                except Exception as e:
                    st.error(f"GitHub Error: {e}")

        # -------------------------
        # Private Mini-Games
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
            gta_url = "https://www.hero-wars.com/?hl=en"
            st.markdown(f"[Play GTA-style Game]({gta_url})")
            components.iframe(gta_url, width=1000, height=600)
            st.markdown("Other mini-games coming soon!")
    else:
        st.info("Enter editor password to access this section.")
