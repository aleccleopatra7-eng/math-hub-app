import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import qrcode
from PIL import Image

st.title("Interactive Math Hub")

# -------------------------
# Sidebar options
# -------------------------

st.sidebar.title("Select Tool")

tool = st.sidebar.selectbox(
    "Choose a Topic",
    ("LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations")
)

# -------------------------
# LCM AND GCD
# -------------------------

if tool == "LCM & GCD":

    st.header("LCM & GCD Visualizer")

    a = st.number_input("Enter Number 1", value=6)
    b = st.number_input("Enter Number 2", value=8)

    if st.button("Calculate"):

        gcd = math.gcd(a,b)
        lcm = a*b//gcd

        st.write("GCD =", gcd)
        st.write("LCM =", lcm)

        multiples_a=[a*i for i in range(1,10)]
        multiples_b=[b*i for i in range(1,10)]

        factors_a=[i for i in range(1,a+1) if a%i==0]
        factors_b=[i for i in range(1,b+1) if b%i==0]

        fig,ax=plt.subplots()

        ax.scatter(multiples_a,[3]*len(multiples_a),label="Multiples A ⭐")
        ax.scatter(multiples_b,[4]*len(multiples_b),label="Multiples B ⭐")

        ax.scatter(factors_a,[1]*len(factors_a),marker="s",label="Factors A ⬛")
        ax.scatter(factors_b,[2]*len(factors_b),marker="s",label="Factors B ⬛")

        ax.scatter(lcm,3.5,color="green",s=120,label="LCM")
        ax.scatter(gcd,0.5,color="orange",s=120,label="GCD")

        # Label points
        for x in multiples_a:
            ax.text(x,3.05,str(x),ha="center")

        for x in multiples_b:
            ax.text(x,4.05,str(x),ha="center")

        for x in factors_a:
            ax.text(x,1.05,str(x),ha="center")

        for x in factors_b:
            ax.text(x,2.05,str(x),ha="center")

        ax.set_yticks([0.5,1,2,3,3.5,4])
        ax.set_yticklabels(["GCD","Factors A","Factors B","Multiples A","LCM","Multiples B"])

        ax.grid(True)
        ax.legend()

        st.pyplot(fig)
# -------------------------
# PRIME FACTORS
# -------------------------

elif tool == "Prime Factors":

    st.header("Prime Factorization")

    n = st.number_input("Enter Number", value=24)

    if st.button("Find Prime Factors"):

        factors=[]
        d=2

        while n>1:
            while n%d==0:
                factors.append(d)
                n=n/d
            d+=1

        st.write("Prime Factors:", factors)

# -------------------------
# RATIOS
# -------------------------

elif tool == "Ratios":

    st.header("Ratio Simplifier")

    a = st.number_input("First Number",value=4)
    b = st.number_input("Second Number",value=8)

    if st.button("Simplify Ratio"):

        g=math.gcd(a,b)

        st.write("Simplified Ratio =", int(a/g),":",int(b/g))

# -------------------------
# SIMULTANEOUS EQUATIONS
# -------------------------

elif tool == "Simultaneous Equations":

    st.header("Simultaneous Equation Solver")

    a1=st.number_input("a1",value=2)
    b1=st.number_input("b1",value=3)
    c1=st.number_input("c1",value=11)

    a2=st.number_input("a2",value=1)
    b2=st.number_input("b2",value=-1)
    c2=st.number_input("c2",value=1)

    # Show the equations generated
    st.subheader("Generated Equations")

    st.write(f"{a1}x + {b1}y = {c1}")
    st.write(f"{a2}x + {b2}y = {c2}")

    if st.button("Solve"):

        det=a1*b2-a2*b1

        if det!=0:

            x=(c1*b2-c2*b1)/det
            y=(a1*c2-a2*c1)/det

            st.success(f"Solution: x = {x}, y = {y}")

            x_vals=np.linspace(-10,10,400)

            y1=(c1-a1*x_vals)/b1
            y2=(c2-a2*x_vals)/b2

            fig,ax=plt.subplots()

            ax.plot(x_vals,y1,label=f"{a1}x + {b1}y = {c1}")
            ax.plot(x_vals,y2,label=f"{a2}x + {b2}y = {c2}")

            ax.scatter(x,y,color="red",s=120)

            ax.grid(True)
            ax.legend()

            st.pyplot(fig)

        else:

            st.error("No unique solution")

# -------------------------
# QR CODE
# -------------------------

elif tool == "QR Code":

    st.header("QR Code Generator")

    link = st.text_input("Enter Link")

    if st.button("Generate QR"):

        qr=qrcode.make(link)

        st.image(qr)
