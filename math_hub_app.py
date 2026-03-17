import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from fractions import Fraction
from github import Github
import openai

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")
st.title("📊 Interactive Math Hub")

# -------------------------
# CREATE FOLDERS
# -------------------------
folders = ["submissions","approved","inbox","feedback"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# -------------------------
# SESSION STATE
# -------------------------
if "teacher_logged_in" not in st.session_state:
    st.session_state.teacher_logged_in = False
if "editor_logged_in" not in st.session_state:
    st.session_state.editor_logged_in = False
if "special_verified" not in st.session_state:
    st.session_state.special_verified = False

# -------------------------
# LOAD TEACHERS
# -------------------------
if os.path.exists("teachers.json"):
    with open("teachers.json","r") as f:
        teacher_data = json.load(f)
else:
    teacher_data = {}

# -------------------------
# SECRETS
# -------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN","")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY","")
openai.api_key = OPENAI_API_KEY
EDITOR_PASSWORD = "aceluffy"

# -------------------------
# USER TYPE
# -------------------------
user_type = st.radio("I am a:", ["Learner","Teacher","Editor"])

# =====================================================
# TOPIC LIST
# =====================================================
topics = ["LCM & GCD","Prime Factors","Ratios","Simultaneous Equations"]

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")
    topic = st.sidebar.selectbox("Choose Topic", topics)

    # -------------------------
    # LCM & GCD
    # -------------------------
    if topic == "LCM & GCD":
        st.subheader("LCM & GCD Visualizer")
        a = st.number_input("Number A",1,100,6)
        b = st.number_input("Number B",1,100,8)
        gcd = math.gcd(a,b)
        lcm = a*b//gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")

        factors_a = [i for i in range(1,a+1) if a%i==0]
        factors_b = [i for i in range(1,b+1) if b%i==0]
        multiples_a = [a*i for i in range(1,10)]
        multiples_b = [b*i for i in range(1,10)]

        fig,ax = plt.subplots()
        ax.scatter(factors_a,[1]*len(factors_a), color="orange", label="Factors A")
        ax.scatter(factors_b,[2]*len(factors_b), color="blue", label="Factors B")
        ax.scatter(multiples_a,[3]*len(multiples_a), color="green", label="Multiples A")
        ax.scatter(multiples_b,[4]*len(multiples_b), color="red", label="Multiples B")
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
    # PRIME FACTORS
    # -------------------------
    elif topic == "Prime Factors":
        st.subheader("Prime Factorization Tree")
        n = st.number_input("Enter number",2,100,12)
        factors=[]
        temp=n
        i=2
        tree=[]
        while temp>1:
            if temp%i==0:
                factors.append(i)
                tree.append((temp,i,temp//i))
                temp//=i
            else:
                i+=1
        st.write("Prime factors:", factors)
        st.markdown("**Factor Tree:**")
        for parent,factor,remainder in tree:
            st.write(f"{parent} → {factor} × {remainder}")

    # -------------------------
    # RATIOS
    # -------------------------
    elif topic == "Ratios":
        st.subheader("Simplified Ratios")
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)
        frac = Fraction(a,b)
        st.write(f"Simplified Ratio: {frac.numerator}:{frac.denominator}")

    # -------------------------
    # SIMULTANEOUS EQUATIONS
    # -------------------------
    elif topic == "Simultaneous Equations":
        st.subheader("Simultaneous Equation Solver")
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
                st.error("No unique solution")

    # -------------------------
    # INBOX SYSTEM
    # -------------------------
    st.subheader("📥 Send Request to Teacher")
    name = st.text_input("Your Name")
    code = st.text_input("Teacher Code")
    topic_req = st.text_input("Topic")
    msg = st.text_area("Message")

    if st.button("Send Request"):
        if name and code and msg:
            file = f"inbox/{code}.json"
            if os.path.exists(file):
                with open(file,"r") as f:
                    data=json.load(f)
            else:
                data=[]
            data.append({"name":name,"topic":topic_req,"message":msg})
            with open(file,"w") as f:
                json.dump(data,f)
            st.success("Sent!")
        else:
            st.error("Fill all fields")

    # -------------------------
    # FEEDBACK SYSTEM
    # -------------------------
    st.subheader("⭐ Rate This App")
    rating = st.slider("Rate (1-5)",1,5,3)
    comment = st.text_area("Comment")
    suggestion = st.text_area("Suggestions")

    if st.button("Submit Feedback"):
        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
        else:
            data=[]
        data.append({"rating":rating,"comment":comment,"suggestion":suggestion})
        with open(file,"w") as f:
            json.dump(data,f)
        st.success("Thanks for feedback!")

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
        st.subheader("📬 Student Requests")
        file=f"inbox/{code}.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
            for d in data:
                st.write(d["name"], "-", d["topic"])
                st.write(d["message"])
                st.write("------")
        else:
            st.info("No requests")

        st.subheader("⭐ Feedback")
        file="feedback/feedback.json"
        if os.path.exists(file):
            with open(file,"r") as f:
                data=json.load(f)
            avg = sum([d["rating"] for d in data])/len(data)
            st.success(f"Average Rating: {round(avg,2)} ⭐")
            for d in data:
                st.write("Rating:", d["rating"])
                st.write("Comment:", d["comment"])
                st.write("Suggestion:", d["suggestion"])
                st.write("------")
        else:
            st.info("No feedback yet")

        st.subheader("📤 Submit Topic to Editor")
        topic_name = st.text_input("Topic Name")
        topic_desc = st.text_area("Description")

        if st.button("Submit Topic"):
            if topic_name and topic_desc:
                data = {"topic_name":topic_name,"topic_description":topic_desc}
                file=f"submissions/{topic_name.replace(' ','_')}.json"
                with open(file,"w") as f:
                    json.dump(data,f)
                st.success("Submitted!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type=="Editor":
    st.header("Editor Section")
    password = st.text_input("Enter Password", type="password")

    if password == EDITOR_PASSWORD:
        st.session_state.editor_logged_in = True

    if st.session_state.editor_logged_in:
        st.success("Access Granted")

        # -------------------------
        # SPECIAL QUESTION LOCK
        # -------------------------
        if not st.session_state.special_verified:
            st.subheader("🔐 Answer to Access Games")
            answer = st.text_input("who is my chizi?")
            if st.button("Submit Answer"):
                if answer.lower().strip() == "riya":
                    st.session_state.special_verified = True
                    st.success("Access to games granted 🎮")
                else:
                    st.error("Wrong answer")
        else:
            st.subheader("🎮 Mini Games Section")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
            st.info("More games coming soon!")

        # -------------------------
        # MAIN EDITOR WORK
        # -------------------------
        st.subheader("📂 Topic Management")
        repo_name = st.text_input("GitHub Repo (username/repo)")
        files = glob.glob("submissions/*.json")
        for file in files:
            with open(file,"r") as f:
                data=json.load(f)
            st.write("Topic:", data["topic_name"])
            st.write("Description:", data["topic_description"])
            if st.button(f"Generate Code for {data['topic_name']}"):
                if OPENAI_API_KEY:
                    prompt = f"Generate python code for {data['topic_description']}"
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        max_tokens=500
                    )
                    code = response.choices[0].text
                    data["code"] = code
                    with open(file,"w") as f:
                        json.dump(data,f)
                    st.code(code)
                else:
                    st.error("No OpenAI key")
            if st.button(f"Push {data['topic_name']}"):
                if repo_name and data.get("code"):
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(repo_name)
                    filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                    repo.create_file(filename,"Add topic",data["code"])
                    os.rename(file,f"approved/{os.path.basename(file)}")
                    st.success("Pushed to GitHub")
