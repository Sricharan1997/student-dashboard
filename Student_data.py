import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="EduMetrics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# LOAD DATA
# =========================
DATA_PATH = "data/student_data2.csv"
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

# Color coding for bars
grade_colors = {"A":"#2ECC71", "B":"#F1C40F", "C":"#E67E22", "D":"#E74C3C"}
df["Color"] = df["Grade"].map(grade_colors)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🎛 Filter Students")
subject = st.sidebar.selectbox("Subject to Analyze", subjects + ["Average_Score"])
grades = st.sidebar.multiselect("Select Grades", df["Grade"].unique(), df["Grade"].unique())
attendance = st.sidebar.multiselect(
    "Attendance Level",
    df["Attendance_Level"].unique(),
    df["Attendance_Level"].unique()
)

if st.sidebar.button("🔄 Reset Filters"):
    st.experimental_rerun()

filtered = df[df["Grade"].isin(grades) & df["Attendance_Level"].isin(attendance)]

# =========================
# KPI METRICS
# =========================
st.title("🎓 EduMetrics Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", len(filtered))
col2.metric("Average Score", round(filtered["Average_Score"].mean(), 2))
col3.metric("Top Score", filtered["Average_Score"].max())
col4.metric("Avg Attendance", f"{round(filtered['Attendance'].mean(),1)}%")

st.markdown("---")

# =========================
# MAIN TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Performance Analysis", 
    "🔍 Correlation", 
    "📉 Grade Trends", 
    "📚 Subject Insights"
])

# =========================
# OVERVIEW TAB
# =========================
with tab1:
    st.subheader("Distribution of Students by Scores & Grades")
    col1, col2 = st.columns(2)

    fig_hist = px.histogram(
        filtered, x=subject, nbins=20,
        color="Grade", color_discrete_map=grade_colors,
        hover_data=["Name", "Grade"], labels={subject:subject},
        title=f"{subject} Distribution"
    )
    fig_hist.update_layout(template="plotly_white", dragmode="zoom")
    col1.plotly_chart(fig_hist, use_container_width=True)

    fig_pie = px.pie(
        filtered, names="Grade", values="Average_Score",
        title="Grade Distribution", hole=0.4,
        color="Grade", color_discrete_map=grade_colors
    )
    fig_pie.update_traces(textinfo="percent+label")
    col2.plotly_chart(fig_pie, use_container_width=True)

# =========================
# PERFORMANCE ANALYSIS TAB
# =========================
with tab2:
    st.subheader("Attendance vs Performance & Top/Bottom Students")
    col1, col2 = st.columns(2)

    # Scatter plot
    fig_scatter = px.scatter(
        filtered, x="Attendance", y="Average_Score", color="Grade",
        size="Average_Score", hover_name="Name",
        labels={"Attendance":"Attendance %"}, title="Attendance vs Average Score",
        color_discrete_map=grade_colors
    )
    fig_scatter.update_layout(template="plotly_white", dragmode="zoom")
    col1.plotly_chart(fig_scatter, use_container_width=True)

    # Top & Bottom 10 students
    top10 = filtered.sort_values("Average_Score", ascending=False).head(10)
    bottom10 = filtered.sort_values("Average_Score", ascending=True).head(10)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=top10["Name"], y=top10["Average_Score"],
        name="Top 10", marker_color="#2ECC71", text=top10["Average_Score"], textposition="auto"
    ))
    fig_bar.add_trace(go.Bar(
        x=bottom10["Name"], y=bottom10["Average_Score"],
        name="Bottom 10", marker_color="#E74C3C", text=bottom10["Average_Score"], textposition="auto"
    ))
    fig_bar.update_layout(title="Top & Bottom 10 Students", template="plotly_white", barmode="group")
    col2.plotly_chart(fig_bar, use_container_width=True)

# =========================
# CORRELATION TAB
# =========================
with tab3:
    st.subheader("Correlation Heatmap")
    corr = filtered[subjects + ["Attendance"]].corr()
    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="Correlation Heatmap"
    )
    fig_corr.update_layout(template="plotly_white")
    st.plotly_chart(fig_corr, use_container_width=True)

# =========================
# GRADE TRENDS TAB
# =========================
with tab4:
    st.subheader("Grade Trends")
    grade_counts = filtered["Grade"].value_counts().sort_index()
    fig_grade = px.bar(
        x=grade_counts.index, y=grade_counts.values,
        labels={"x":"Grade", "y":"Number of Students"},
        title="Number of Students per Grade",
        color=grade_counts.index.map(grade_colors)
    )
    fig_grade.update_layout(template="plotly_white")
    st.plotly_chart(fig_grade, use_container_width=True)

# =========================
# SUBJECT INSIGHTS TAB
# =========================
with tab5:
    st.subheader("Subject Score Distributions")
    col1, col2, col3 = st.columns(3)

    for i, subj in enumerate(subjects):
        fig_box = px.box(
            filtered, y=subj, color="Grade", color_discrete_map=grade_colors,
            title=f"{subj} Score Distribution", points="all"
        )
        if i == 0:
            col1.plotly_chart(fig_box, use_container_width=True)
        elif i == 1:
            col2.plotly_chart(fig_box, use_container_width=True)
        else:
            col3.plotly_chart(fig_box, use_container_width=True)

# =========================
# DATA TABLE & DOWNLOAD
# =========================
with st.expander("📄 View & Download Filtered Data"):
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="filtered_students.csv", mime="text/csv")

st.success("✅ Dashboard fully interactive & data-scientist ready!")
