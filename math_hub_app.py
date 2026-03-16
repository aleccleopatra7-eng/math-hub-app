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
SPECIAL_ANSWER = "me"

# -------------------------
# USER TYPE SELECTION
# -------------------------
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# -------------------------
# LEARNER SECTION (with chat checkboxes)
# -------------------------
if user_type == "Learner":
    st.header("Learner Section")
    default_topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    dynamic_topics = [os.path.basename(f).replace(".py","').replace("_"," ") for f in glob.glob("topics/*.py")]
    topic = st.sidebar.selectbox("Choose Topic", default_topics + dynamic_topics)

    learner_name = st.text_input("Your Name", key="learner_name")

    colors = {"Factors A":"#E69F00","Factors B":"#56B4E9","Multiples A":"#009E73","Multiples B":"#D55E00","LCM":"#0072B2","GCD":"#F0E442"}

    # LCM & GCD and Simultaneous Equations code here (same as previous snippet)

    # Chat Options
    st.subheader("Chat Options")
    chat_choices = st.multiselect("Select Chat Type", ["1:1 Teacher Chat", "Group Chat"])

    if "1:1 Teacher Chat" in chat_choices:
        teacher_code = st.text_input("Teacher Code for 1:1 Chat", key="teacher_code_1on1")
        chat_file_1on1 = f"messages/{teacher_code}.json"
        if os.path.exists(chat_file_1on1):
            with open(chat_file_1on1,"r") as f:
                chat_1on1 = json.load(f)
        else:
            chat_1on1 = {"members":[],"messages":[]}
            with open(chat_file_1on1,"w") as f:
                json.dump(chat_1on1,f)

        if learner_name.strip() and learner_name not in chat_1on1["members"]:
            chat_1on1["members"].append(learner_name)
            with open(chat_file_1on1,"w") as f:
                json.dump(chat_1on1,f)

        st.subheader("1:1 Teacher Chat")
        for msg in chat_1on1.get("messages",[]):
            st.write(f"{msg['sender']}: {msg['message']}")

        new_msg_1on1 = st.text_input("Message for 1:1 Chat", key="msg_1on1")
        if st.button("Send 1:1 Message", key=f"send1_{learner_name}_{teacher_code}"):
            if new_msg_1on1.strip():
                chat_1on1["messages"].append({"sender": learner_name,"message": new_msg_1on1})
                with open(chat_file_1on1,"w") as f:
                    json.dump(chat_1on1,f)
                st.experimental_rerun()

    if "Group Chat" in chat_choices:
        group_teacher_code = st.text_input("Teacher Code for Group Chat", key="group_teacher_code")
        group_name = st.text_input("Group Name", key="group_name_input")
        group_file = f"groups/{group_teacher_code}_{group_name}.json"

        if os.path.exists(group_file):
            with open(group_file,"r") as f:
                group_data = json.load(f)
        else:
            group_data = {"teacher": group_teacher_code, "members": [], "messages":[]}
            with open(group_file,"w") as f:
                json.dump(group_data,f)

        if learner_name.strip() and learner_name not in group_data["members"]:
            group_data["members"].append(learner_name)
            with open(group_file,"w") as f:
                json.dump(group_data,f)

        st.subheader(f"Group Chat: {group_name}")
        for msg in group_data.get("messages",[]):
            st.write(f"{msg['sender']}: {msg['message']}")

        new_msg_group = st.text_input("Message for Group Chat", key="msg_group")
        if st.button("Send Group Message", key=f"send_group_{learner_name}_{group_name}"):
            if new_msg_group.strip():
                group_data["messages"].append({"sender": learner_name, "message": new_msg_group})
                with open(group_file,"w") as f:
                    json.dump(group_data,f)
                st.experimental_rerun()

# -------------------------
# TEACHER SECTION
# -------------------------
elif user_type == "Teacher":
    st.header("Teacher Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    teacher_code = st.text_input("Your Teacher Code")

    if st.button("Register / Login"):
        if username not in teacher_data:
            teacher_data[username] = password
            with open(PASSWORD_FILE,"w") as f:
                json.dump(teacher_data,f)
            st.success("Registered successfully!")
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_name = username
        elif teacher_data[username] == password:
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
                        json.dump({"teacher": username,"members": [],"messages":[]},f)
                    st.success(f"Group '{group_name}' created with code '{teacher_code}'")
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

        new_msg = st.text_input("Message to Group")
        if st.button("Send to Group"):
            if new_msg.strip():
                group_data["messages"].append({"sender": username, "message": new_msg})
                with open(chat_file,"w") as f:
                    json.dump(group_data,f)
                st.experimental_rerun()

        st.subheader("Group Messages")
        for msg in group_data.get("messages",[]):
            st.write(f"{msg['sender']}: {msg['message']}")

        st.subheader("Submit Topic Description")
        topic_name = st.text_input("Topic Name")
        topic_description = st.text_area("Topic Description")
        if st.button("Submit Topic"):
            if topic_name.strip() and topic_description.strip():
                submission = {"teacher": username,"teacher_code": teacher_code,"topic_name": topic_name,"topic_description": topic_description}
                filename = f"submissions/{topic_name.replace(' ','_')}.json"
                with open(filename,"w") as f:
                    json.dump(submission,f)
                st.success("Topic submitted for editor approval!")

# -------------------------
# EDITOR SECTION
# -------------------------
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
            with open(file,"r") as f:
                data = json.load(f)
            st.write("Teacher:", data.get("teacher",""))
            st.write("Topic Name:", data.get("topic_name",""))
            st.write("Description:", data.get("topic_description",""))
            st.code(data.get("topic_code",""))

            generate_key = f"generate_{data.get('topic_name','')}_{file}"
            push_key = f"push_{data.get('topic_name','')}_{file}"

            if st.button(f"Generate Code for {data.get('topic_name','')}", key=generate_key):
                if OPENAI_API_KEY and data.get("topic_description","".strip()):
                    try:
                        prompt = f"Generate a Python code snippet for this topic:\n{data['topic_description']}"
                        response = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=500)
                        generated_code = response.choices[0].text.strip()
                        data["topic_code"] = generated_code
                        with open(file,"w") as f:
                            json.dump(data,f)
                        st.code(generated_code)
                        st.success("Code generated successfully!")
                    except Exception as e:
                        st.error(f"OpenAI API Error: {e}")
                else:
                    st.error("Missing API key or topic description!")

            if st.button(f"Approve & Push {data.get('topic_name','')}", key=push_key):
                if not repo_name.strip():
                    st.error("Enter GitHub repo in username/repo format")
                    continue
                try:
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    if os.path.exists(filename):
                        contents = repo.get_contents(filename)
                        repo.update_file(filename,f"Update {data['topic_name']}",data["topic_code"],contents.sha)
                    else:
                        repo.create_file(filename,f"Add {data['topic_name']}",data["topic_code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success(f"Topic '{data['topic_name']}' approved and pushed!")
                except Exception as e:
                    st.error(f"GitHub Error: {e}")

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
            st.success("Access your private games below!")
            gta_url = "https://www.hero-wars.com/?hl=en"
            st.markdown(f"[Play GTA-style Game]({gta_url})")
            components.iframe(gta_url, width=1000, height=600)
            st.markdown("Other mini-games coming soon!")
    else:
        st.info("Enter editor password to access this section.")
