import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# PATHS (Relative for GitHub/Streamlit Cloud)
# =========================
DATA_PATH = "data/student_data2.csv"  # Place CSV inside repo in 'data' folder

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(DATA_PATH)
subjects = ["Math", "Science", "English"]

df["Average_Score"] = df[subjects].mean(axis=1)

def grade(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    return "D"

df["Grade"] = df["Average_Score"].apply(grade)

df["Attendance_Level"] = pd.cut(
    df["Attendance"],
    bins=[0, 80, 90, 100],
    labels=["Low", "Medium", "High"]
)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🎛 Filters")

if st.sidebar.button("🔄 Reset Filters"):
    st.experimental_rerun()

subject = st.sidebar.selectbox("Subject", subjects + ["Average_Score"])
grades = st.sidebar.multiselect("Grade", df["Grade"].unique(), df["Grade"].unique())
attendance = st.sidebar.multiselect(
    "Attendance Level",
    df["Attendance_Level"].unique(),
    df["Attendance_Level"].unique()
)

filtered = df[
    df["Grade"].isin(grades) &
    df["Attendance_Level"].isin(attendance)
]

# =========================
# KPI METRICS
# =========================
st.title("📊 Student Performance Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("👨‍🎓 Students", len(filtered))
col2.metric("📈 Avg Score", round(filtered["Average_Score"].mean(), 2))
col3.metric("🏆 Top Score", filtered["Average_Score"].max())
col4.metric("📊 Avg Attendance", f"{round(filtered['Attendance'].mean(),1)}%")

st.divider()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📌 Overview", "📈 Analysis", "🔗 Correlation"])

# =========================
# OVERVIEW TAB
# =========================
with tab1:
    fig = px.histogram(
        filtered,
        x=subject,
        nbins=20,
        title=f"{subject} Distribution",
        hover_data=["Name", "Grade"],
        range_x=[0, 100]
    )
    fig.update_layout(
        dragmode="zoom",
        hovermode="closest",
        legend=dict(itemclick="toggleothers")
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.pie(
        filtered,
        names="Grade",
        title="Grade Distribution",
        hole=0.4
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# ANALYSIS TAB
# =========================
with tab2:
    fig3 = px.scatter(
        filtered,
        x="Attendance",
        y="Average_Score",
        color="Grade",
        hover_name="Name",
        size="Average_Score",
        range_x=[50, 100],
        range_y=[0, 100],
        title="Attendance vs Performance"
    )
    fig3.update_layout(
        dragmode="zoom",
        hovermode="closest",
        legend=dict(itemclick="toggleothers")
    )
    st.plotly_chart(fig3, use_container_width=True)

    top = filtered.sort_values("Average_Score", ascending=False).head(10)
    fig4 = px.bar(
        top,
        x="Name",
        y="Average_Score",
        text_auto=True,
        title="Top 10 Students"
    )
    fig4.update_layout(
        dragmode="zoom",
        hovermode="closest"
    )
    st.plotly_chart(fig4, use_container_width=True)

# =========================
# CORRELATION TAB
# =========================
with tab3:
    corr = filtered[subjects + ["Attendance"]].corr()
    fig5 = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        title="Correlation Heatmap"
    )
    st.plotly_chart(fig5, use_container_width=True)

# =========================
# DATA TABLE & DOWNLOAD
# =========================
with st.expander("📄 View & Download Data"):
    st.dataframe(filtered, use_container_width=True)
    
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Filtered Data",
        data=csv,
        file_name="filtered_students.csv",
        mime="text/csv"
    )

st.success("✅ Dashboard optimized and ready!")
