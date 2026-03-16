import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# PAGE SETTINGS
# -------------------------

st.set_page_config(
    page_title="Interactive Math Hub",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Interactive Math Hub")
st.write("An interactive platform to explore mathematical concepts visually.")

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("Navigation")

tool = st.sidebar.selectbox(
    "Choose a Topic",
    ("Home", "LCM & GCD", "Prime Factors", "Ratios", "Simultaneous Equations")
)

# -------------------------
# HOME PAGE
# -------------------------

if tool == "Home":

    st.header("Welcome to the Interactive Math Hub")

    st.write("""
This platform allows learners to **explore mathematics interactively**.

### Available Tools

• **LCM & GCD Visualizer**  
• **Prime Factorization Explorer**  
• **Ratio Simplifier**  
• **Simultaneous Equation Solver**

Use the sidebar to start exploring!
""")

# -------------------------
# LCM AND GCD
# -------------------------

elif tool == "LCM & GCD":

    st.header("LCM & GCD Visualizer")

    st.write("""
The **Greatest Common Divisor (GCD)** is the largest number that divides both numbers.

The **Least Common Multiple (LCM)** is the smallest number that both numbers can multiply to reach.
""")

    a = st.slider("Select Number 1", 1, 50, 6)
    b = st.slider("Select Number 2", 1, 50, 8)

    gcd = math.gcd(a, b)
    lcm = a * b // gcd

    st.success(f"GCD = {gcd}")
    st.success(f"LCM = {lcm}")

    st.subheader("Dynamic Number Line")

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

# -------------------------
# PRIME FACTORS
# -------------------------

elif tool == "Prime Factors":

    st.header("Prime Factorization")

    st.write("Prime factorization breaks a number into **prime numbers multiplied together**.")

    num = int(st.number_input("Enter a number", value=24))

    def prime_factors(n):
        factors = []
        d = 2
        while n > 1:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        return factors

    if st.button("Generate Prime Factors"):

        factors = prime_factors(num)

        st.success(f"Prime Factors: {factors}")

        st.subheader("Factor Tree")

        fig, ax = plt.subplots()

        ax.text(0.5, 0.9, str(num), ha="center", fontsize=16)

        y = 0.7
        x_start = 0.3

        for i, f in enumerate(factors):
            ax.text(x_start + i * 0.15, y, str(f), ha="center")

        ax.axis("off")

        st.pyplot(fig)

# -------------------------
# RATIOS
# -------------------------

elif tool == "Ratios":

    st.header("Ratio Simplifier")

    st.write("Ratios compare two quantities.")

    a = st.number_input("First Number", value=4)
    b = st.number_input("Second Number", value=8)

    if st.button("Simplify Ratio"):

        g = math.gcd(a, b)

        st.success(f"Simplified Ratio = {int(a/g)} : {int(b/g)}")

# -------------------------
# SIMULTANEOUS EQUATIONS
# -------------------------

elif tool == "Simultaneous Equations":

    st.header("Simultaneous Equation Solver")

    st.write("Solve two equations with two unknowns.")

    a1 = st.number_input("a1", value=2)
    b1 = st.number_input("b1", value=3)
    c1 = st.number_input("c1", value=11)

    a2 = st.number_input("a2", value=1)
    b2 = st.number_input("b2", value=-1)
    c2 = st.number_input("c2", value=1)

    st.subheader("Generated Equations")

    st.write(f"{a1}x + {b1}y = {c1}")
    st.write(f"{a2}x + {b2}y = {c2}")

  if st.button("Solve"):

    det = a1*b2 - a2*b1

    if det != 0:

        x = (c1*b2 - c2*b1) / det
        y = (a1*c2 - a2*c1) / det

        st.success(f"Solution: x = {x}, y = {y}")

        # Generate values for table
        x_vals = np.arange(-5, 6)

        y1_vals = (c1 - a1*x_vals) / b1
        y2_vals = (c2 - a2*x_vals) / b2

        # -------------------------
        # TABLE OF VALUES
        # -------------------------

        st.subheader("Table of Values")

        table_data = {
            "x": x_vals,
            "y (Eq1)": y1_vals,
            "y (Eq2)": y2_vals
        }

        st.table(table_data)

        # -------------------------
        # GRAPH
        # -------------------------

        x_graph = np.linspace(-10, 10, 400)

        y1 = (c1 - a1*x_graph) / b1
        y2 = (c2 - a2*x_graph) / b2

        fig, ax = plt.subplots()

        ax.plot(x_graph, y1, label=f"{a1}x + {b1}y = {c1}")
        ax.plot(x_graph, y2, label=f"{a2}x + {b2}y = {c2}")

        ax.scatter(x, y, s=120)

        ax.grid(True)
        ax.legend()

        st.pyplot(fig)

    else:

        st.error("No unique solution")
