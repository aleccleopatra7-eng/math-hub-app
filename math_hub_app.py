import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
from github import Github
import openai
from fractions import Fraction

# -------------------------
# PAGE SETTINGS
# -------------------------
st.set_page_config(page_title="Interactive Math Hub", page_icon="📊")
st.title("📊 Interactive Math Hub")

# -------------------------
# CREATE FOLDERS
# -------------------------
os.makedirs("topics", exist_ok=True)
os.makedirs("submissions", exist_ok=True)
os.makedirs("approved", exist_ok=True)
os.makedirs("inbox", exist_ok=True)
os.makedirs("feedback", exist_ok=True)

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
user_type = st.radio("I am a:", ["Learner", "Teacher", "Editor"])

# =====================================================
# LEARNER SECTION
# =====================================================
if user_type == "Learner":
    st.header("Learner Section")

    topics = ["LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations"]
    topic = st.selectbox("Choose Topic", topics)

    # -------------------------
    # LCM & GCD Visualizer
    # -------------------------
    if topic == "LCM & GCD":
        a = st.number_input("Number A", 1, 100, 6)
        b = st.number_input("Number B", 1, 100, 8)
        gcd = math.gcd(a,b)
        lcm = a*b//gcd
        st.success(f"GCD = {gcd}")
        st.success(f"LCM = {lcm}")

        # Visualize Factors & Multiples
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
    # Ratios (Simplified + Multiples)
    # -------------------------
    elif topic == "Ratios":
        a = st.number_input("Value A",1,100,4)
        b = st.number_input("Value B",1,100,6)
        if b != 0:
            frac = Fraction(a,b)
            st.write(f"Simplified Ratio: {frac.numerator}:{frac.denominator}")

        multiples_limit = st.number_input("Multiples limit",1,20,10)
        fig, ax = plt.subplots()
        ax.scatter([i for i in range(1,multiples_limit+1)],[a*i for i in range(1,multiples_limit+1)], color="orange", label="A multiples")
        ax.scatter([i for i in range(1,multiples_limit+1)],[b*i for i in range(1,multiples_limit+1)], color="blue", label="B multiples")
        ax.set_xlabel("Multiplier")
        ax.set_ylabel("Value")
        ax.set_title(f"Multiples of {a} and {b}")
        ax.legend()
        st.pyplot(fig)

    # -------------------------
    # Prime Factors (Tree)
    # -------------------------
    elif topic == "Prime Factors":
        n = st.number_input("Enter number",2,100,12)
        def prime_factors_tree(n):
            factors = []
            temp = n
            i=2
            while i*i <= temp:
                while temp % i == 0:
                    factors.append(i)
                    temp //= i
                i += 1
            if temp>1:
                factors.append(temp)
            return factors
        factors = prime_factors_tree(n)
        st.write(f"Prime Factors: {factors}")

        # Visual Tree
        def draw_factor_tree(number):
            fig, ax = plt.subplots()
            levels = [(number,0,0)]
            y_gap = -1
            texts=[]
            while levels:
                num,x,y = levels.pop(0)
                for i in range(2,num+1):
                    if num % i ==0:
                        j=num//i
                        ax.plot([x,x-0.5],[y,y+y_gap],color='black')
                        ax.plot([x,x+0.5],[y,y+y_gap],color='black')
                        texts.append((x-0.5,y+y_gap,str(i)))
                        texts.append((x+0.5,y+y_gap,str(j)))
                        levels.append((i,x-0.5,y+y_gap))
                        levels.append((j,x+0.5,y+y_gap))
                        break
            ax.text(0,0,str(number),ha='center',va='center',bbox=dict(facecolor='yellow', alpha=0.5))
            for x,y,text in texts:
                ax.text(x,y,text,ha='center',va='center',bbox=dict(facecolor='lightblue', alpha=0.5))
            ax.axis('off')
            st.pyplot(fig)
        draw_factor_tree(n)

    # -------------------------
    # Simultaneous Equations
    # -------------------------
    elif topic == "Simultaneous Equations":
        a1 = st.number_input("a1", value=2)
        b1 = st.number_input("b1", value=3)
        c1 = st.number_input("c1", value=11)
        a2 = st.number_input("a2", value=1)
        b2 = st.number_input("b2", value=-1)
        c2 = st.number_input("c2", value=1)

        if st.button("Solve"):
            det = a1*b2 - a2*b1
            if det != 0:
                x = (c1*b2 - c2*b1)/det
                y = (a1*c2 - a2*c1)/det
                st.success(f"x={x}, y={y}")

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
                st.error("No unique solution")

    # -------------------------
    # Inbox & Feedback
    # -------------------------
    st.subheader("📥 Send Request to Teacher")
    name = st.text_input("Your Name")
    code = st.text_input("Teacher Code")
    topic_req = st.text_input("Topic")
    msg = st.text_area("Message")
    if st.button("Send Request"):
        if name and code and msg:
            file=f"inbox/{code}.json"
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
            # =====================================================
# TEACHER SECTION
# =====================================================
elif user_type == "Teacher":
    st.header("Teacher Section")

    username = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    code = st.text_input("Your Teacher Code")

    if st.button("Login/Register"):
        if username not in teacher_data:
            teacher_data[username] = pwd
            with open("teachers.json","w") as f:
                json.dump(teacher_data,f)
            st.success("Registered successfully!")
            st.session_state.teacher_logged_in = True
        elif teacher_data[username] == pwd:
            st.success("Logged in successfully!")
            st.session_state.teacher_logged_in = True
        else:
            st.error("Wrong password!")

    if st.session_state.teacher_logged_in:
        st.subheader("📬 Student Requests")
        inbox_file = f"inbox/{code}.json"
        if os.path.exists(inbox_file):
            with open(inbox_file,"r") as f:
                requests = json.load(f)
            if requests:
                st.table([[r["name"], r["topic"], r["message"]] for r in requests])
            else:
                st.info("No requests yet.")
        else:
            st.info("No requests yet.")

        st.subheader("⭐ Feedback")
        feedback_file = "feedback/feedback.json"
        if os.path.exists(feedback_file):
            with open(feedback_file,"r") as f:
                feedbacks = json.load(f)
            if feedbacks:
                avg_rating = sum([f["rating"] for f in feedbacks])/len(feedbacks)
                st.success(f"Average Rating: {round(avg_rating,2)} ⭐")
                st.table([[f["rating"], f["comment"], f["suggestion"]] for f in feedbacks])
            else:
                st.info("No feedback yet.")
        else:
            st.info("No feedback yet.")

        st.subheader("📤 Submit Topic to Editor")
        topic_name = st.text_input("Topic Name")
        topic_desc = st.text_area("Description")
        if st.button("Submit Topic"):
            if topic_name and topic_desc:
                submission = {"teacher": username, "teacher_code": code, "topic_name": topic_name, "topic_description": topic_desc}
                file = f"submissions/{topic_name.replace(' ','_')}.json"
                with open(file,"w") as f:
                    json.dump(submission,f)
                st.success("Topic submitted to editor for approval!")

# =====================================================
# EDITOR SECTION
# =====================================================
elif user_type == "Editor":
    st.header("Editor Section")

    password = st.text_input("Enter Password", type="password")
    if password == EDITOR_PASSWORD:
        st.session_state.editor_logged_in = True

    if st.session_state.editor_logged_in:
        st.success("Access Granted ✅")

        # -------------------------
        # SPECIAL QUESTION LOCK (Mini Games)
        # -------------------------
        if not st.session_state.special_verified:
            st.subheader("🔐 Answer to Access Games")
            answer = st.text_input("Who is my chizi?")
            if st.button("Submit Answer"):
                if answer.lower().strip() == "riya":
                    st.session_state.special_verified = True
                    st.success("Access to mini-games granted 🎮")
                else:
                    st.error("Wrong answer!")
        else:
            st.subheader("🎮 Mini Games")
            st.markdown("[Play Game](https://www.hero-wars.com/?hl=en)")
            st.info("More games coming soon!")

        # -------------------------
        # Topic Management (Visual)
        # -------------------------
        st.subheader("📂 Approve & Generate Code")

        repo_name = st.text_input("GitHub Repo (username/repo)")

        submissions = glob.glob("submissions/*.json")
        for file in submissions:
            with open(file,"r") as f:
                data = json.load(f)
            st.markdown(f"**Topic:** {data.get('topic_name','')}")
            st.markdown(f"**Description:** {data.get('topic_description','')}")

            # Generate Python Code using OpenAI
            gen_key = f"generate_{data.get('topic_name')}"
            if st.button(f"Generate Code for {data.get('topic_name')}", key=gen_key):
                if OPENAI_API_KEY:
                    prompt = f"Generate a Python code snippet for the following topic:\n{data.get('topic_description')}"
                    try:
                        response = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=prompt,
                            max_tokens=500
                        )
                        code = response.choices[0].text.strip()
                        data["topic_code"] = code
                        with open(file,"w") as f:
                            json.dump(data,f)
                        st.code(code)
                        st.success("Code generated successfully!")
                    except Exception as e:
                        st.error(f"OpenAI Error: {e}")
                else:
                    st.error("OpenAI API Key not set!")

            # Push to GitHub
            push_key = f"push_{data.get('topic_name')}"
            if st.button(f"Approve & Push {data.get('topic_name')}", key=push_key):
                if not repo_name.strip():
                    st.error("Enter GitHub repo as username/repo")
                else:
                    try:
                        g = Github(GITHUB_TOKEN)
                        repo = g.get_repo(repo_name)
                        filename = f"topics/{data['topic_name'].replace(' ','_')}.py"
                        if os.path.exists(filename):
                            contents = repo.get_contents(filename)
                            repo.update_file(filename,f"Update topic {data['topic_name']}",data.get("topic_code",""),contents.sha)
                        else:
                            repo.create_file(filename,f"Add topic {data['topic_name']}",data.get("topic_code",""))
                        os.rename(file,f"approved/{os.path.basename(file)}")
                        st.success(f"Topic '{data['topic_name']}' approved and pushed!")
                    except Exception as e:
                        st.error(f"GitHub Error: {e}")
        st.success("Thanks for feedback!")
