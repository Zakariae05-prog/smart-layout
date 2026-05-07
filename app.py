import streamlit as st
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Smart Warehouse 4.0",
    layout="wide"
)

st.title("🏭 AI Smart Warehouse 4.0")
st.markdown("### Intelligent Logistics & Industry 4.0 Platform")

# =====================================================
# SESSION STATE
# =====================================================
if "data" not in st.session_state:

    st.session_state.data = pd.DataFrame({
        "Product": ["A", "B", "C", "D", "E"],
        "X": [3, 5, 2, 8, 6],
        "Y": [1, 2, 6, 3, 7],
        "Stock": [20, 15, 30, 12, 18],
        "Defect_rate": [0.1, 0.05, 0.2, 0.08, 0.12]
    })

if "history" not in st.session_state:
    st.session_state.history = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "order_path" not in st.session_state:
    st.session_state.order_path = []

if "time_saved" not in st.session_state:
    st.session_state.time_saved = 0

if "distance_saved" not in st.session_state:
    st.session_state.distance_saved = 0

if "cost_saved" not in st.session_state:
    st.session_state.cost_saved = 0

if "co2_saved" not in st.session_state:
    st.session_state.co2_saved = 0

data = st.session_state.data

# =====================================================
# DISTANCE FUNCTION
# =====================================================
def distance(a, b):

    return math.sqrt(
        (a[0] - b[0])**2 +
        (a[1] - b[1])**2
    )

# =====================================================
# TOTAL DISTANCE
# =====================================================
def total_distance(path, df):

    current = (0, 0)
    total = 0

    for p in path:

        row = df[df["Product"] == p].iloc[0]

        pos = (row["X"], row["Y"])

        total += distance(current, pos)

        current = pos

    return round(total, 2)

# =====================================================
# AI PICKING OPTIMIZATION
# =====================================================
def optimize_path(order_list, df):

    current = (0, 0)

    remaining = order_list.copy()

    path = []

    while remaining:

        nearest = None
        min_distance = float("inf")

        for p in remaining:

            row = df[df["Product"] == p].iloc[0]

            pos = (row["X"], row["Y"])

            d = distance(current, pos)

            if d < min_distance:

                min_distance = d

                nearest = p

        path.append(nearest)

        row = df[df["Product"] == nearest].iloc[0]

        current = (row["X"], row["Y"])

        remaining.remove(nearest)

    return path

# =====================================================
# DEMAND ANALYSIS
# =====================================================
def analyze_demand(history):

    demand = {}

    for p in history:

        demand[p] = demand.get(p, 0) + 1

    return demand

# =====================================================
# AI DYNAMIC LAYOUT
# =====================================================
def optimize_layout(df, demand):

    if not demand:
        return df

    sorted_products = sorted(
        demand.items(),
        key=lambda x: x[1],
        reverse=True
    )

    best_positions = [
        (0,0),
        (1,0),
        (0,1),
        (1,1),
        (2,0)
    ]

    df = df.copy()

    for i, (product, _) in enumerate(sorted_products):

        if i < len(best_positions):

            df.loc[
                df["Product"] == product,
                "X"
            ] = best_positions[i][0]

            df.loc[
                df["Product"] == product,
                "Y"
            ] = best_positions[i][1]

    return df

# =====================================================
# MACHINE LEARNING DEMAND PREDICTION
# =====================================================
def predict_demand(history, products):

    predictions = {}

    for product in products:

        occurrences = [
            1 if h == product else 0
            for h in history
        ]

        if len(occurrences) < 2:

            predictions[product] = random.randint(1, 5)

        else:

            X = np.array(range(len(occurrences))).reshape(-1, 1)

            y = np.array(occurrences)

            model = LinearRegression()

            model.fit(X, y)

            future = np.array([[len(occurrences) + 1]])

            pred = model.predict(future)[0]

            predictions[product] = round(
                max(pred * 10, 0),
                2
            )

    return predictions

# =====================================================
# KPI DASHBOARD
# =====================================================
st.subheader("📊 AI Dashboard KPI")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "📦 Total Stock",
    int(data["Stock"].sum())
)

col2.metric(
    "📦 Products",
    len(data)
)

col3.metric(
    "⏱ Time Saved",
    f"{round(st.session_state.time_saved,2)} sec"
)

col4.metric(
    "💰 Cost Saved",
    f"{round(st.session_state.cost_saved,2)} €"
)

col5.metric(
    "🌱 CO₂ Reduced",
    f"{round(st.session_state.co2_saved,2)} kg"
)

st.dataframe(data)

# =====================================================
# ORDER SECTION
# =====================================================
st.subheader("🛒 Smart Picking Order")

order = st.multiselect(
    "Select products",
    data["Product"].tolist()
)

if st.button("🚀 Generate AI Picking"):

    if not order:

        st.warning("Select at least one product")

    else:

        normal_path = order

        ai_path = optimize_path(order, data)

        normal_distance = total_distance(
            normal_path,
            data
        )

        ai_distance = total_distance(
            ai_path,
            data
        )

        distance_saved = normal_distance - ai_distance

        time_saved = distance_saved * 2

        cost_saved = distance_saved * 0.5

        co2_saved = distance_saved * 0.2

        st.session_state.order_path = ai_path

        st.session_state.distance_saved = distance_saved

        st.session_state.time_saved = time_saved

        st.session_state.cost_saved = cost_saved

        st.session_state.co2_saved = co2_saved

        st.success("✅ AI Picking Optimized")

        st.write("### 🤖 AI Optimized Path")
        st.write(" ➜ ".join(ai_path))

        st.write(f"📏 Normal Distance : {normal_distance}")
        st.write(f"📏 AI Distance : {ai_distance}")

        st.write(
            f"⏱ Estimated Time Saved : "
            f"{round(time_saved,2)} sec"
        )

# =====================================================
# QR SCAN
# =====================================================
st.subheader("📡 IoT Smart Scan")

scan_product = st.selectbox(
    "Scan Product",
    data["Product"].tolist()
)

if st.button("📡 Scan"):

    row = data[
        data["Product"] == scan_product
    ].iloc[0]

    defect = random.random() < row["Defect_rate"]

    st.session_state.history.append(scan_product)

    if defect:

        alert = f"❌ DEFECT DETECTED : {scan_product}"

        st.session_state.alerts.append(alert)

        st.error(alert)

    else:

        st.success(f"✅ {scan_product} Valid")

        st.session_state.data.loc[
            st.session_state.data["Product"]
            == scan_product,
            "Stock"
        ] -= 1

# =====================================================
# AI LAYOUT OPTIMIZATION
# =====================================================
if st.button("🔄 AI Layout Optimization"):

    demand = analyze_demand(
        st.session_state.history
    )

    st.session_state.data = optimize_layout(
        st.session_state.data,
        demand
    )

    st.success(
        "🏭 Warehouse Automatically Reorganized"
    )

# =====================================================
# DEMAND ANALYSIS
# =====================================================
st.subheader("📈 Demand Analysis")

if st.session_state.history:

    demand = analyze_demand(
        st.session_state.history
    )

    st.bar_chart(demand)

else:

    st.info("No history yet")

# =====================================================
# AI DEMAND PREDICTION
# =====================================================
st.subheader("🧠 AI Demand Prediction")

predictions = predict_demand(
    st.session_state.history,
    data["Product"].tolist()
)

pred_df = pd.DataFrame({
    "Product": list(predictions.keys()),
    "Predicted Demand": list(predictions.values())
})

st.dataframe(pred_df)

st.line_chart(
    pred_df.set_index("Product")
)

# =====================================================
# HEATMAP LAYOUT
# =====================================================
st.subheader("🔥 AI Warehouse Heatmap")

fig, ax = plt.subplots(figsize=(8,6))

history_demand = analyze_demand(
    st.session_state.history
)

for _, row in st.session_state.data.iterrows():

    demand_level = history_demand.get(
        row["Product"],
        1
    )

    ax.scatter(
        row["X"],
        row["Y"],
        s=700,
        c=demand_level,
        cmap="RdYlGn_r"
    )

    ax.text(
        row["X"],
        row["Y"],
        row["Product"],
        ha='center',
        va='center',
        fontsize=12,
        color='black'
    )

ax.set_title("AI Dynamic Warehouse Heatmap")

ax.grid(True)

st.pyplot(fig)

# =====================================================
# DIGITAL TWIN VISUALIZATION
# =====================================================
st.subheader("🛰 Digital Twin Warehouse")

fig2, ax2 = plt.subplots(figsize=(9,7))

for _, row in st.session_state.data.iterrows():

    ax2.scatter(
        row["X"],
        row["Y"],
        s=900
    )

    ax2.text(
        row["X"],
        row["Y"],
        f"{row['Product']}\nStock:{row['Stock']}",
        ha='center',
        va='center',
        fontsize=10
    )

# Draw operator path
if st.session_state.order_path:

    coords_x = [0]
    coords_y = [0]

    for p in st.session_state.order_path:

        row = st.session_state.data[
            st.session_state.data["Product"] == p
        ].iloc[0]

        coords_x.append(row["X"])
        coords_y.append(row["Y"])

    ax2.plot(
        coords_x,
        coords_y,
        linewidth=2
    )

ax2.set_title("Warehouse Digital Twin")

ax2.grid(True)

st.pyplot(fig2)

# =====================================================
# PREDICTIVE MAINTENANCE
# =====================================================
st.subheader("⚙ Predictive Maintenance")

temperature = random.randint(20, 80)

vibration = random.randint(10, 100)

humidity = random.randint(30, 90)

colA, colB, colC = st.columns(3)

colA.metric(
    "🌡 Temperature",
    f"{temperature} °C"
)

colB.metric(
    "📳 Vibration",
    vibration
)

colC.metric(
    "💧 Humidity",
    f"{humidity}%"
)

if temperature > 60:

    st.error(
        "⚠ High Temperature Detected"
    )

if vibration > 80:

    st.error(
        "⚠ Predictive Maintenance Required"
    )

# =====================================================
# ALERTS
# =====================================================
st.subheader("🚨 Smart Alerts")

if st.session_state.alerts:

    for alert in st.session_state.alerts:

        st.warning(alert)

else:

    st.info("No alerts")

# =====================================================
# LAST AI PATH
# =====================================================
st.subheader("🚶 Last AI Path")

if st.session_state.order_path:

    st.write(
        " ➜ ".join(
            st.session_state.order_path
        )
    )

else:

    st.info("No path generated")
