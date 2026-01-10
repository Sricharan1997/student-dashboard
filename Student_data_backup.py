import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import warnings

# =========================
# STREAMLIT CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="Student Performance Dashboard",
    layout="wide"
)

warnings.filterwarnings("ignore")

# =========================
# PATH SETUP
# =========================
BASE_OUTPUT_DIR = r"C:\Users\thota\OneDrive\Documents\Students_performance_Analysis"
DATA_PATH = os.path.join(BASE_OUTPUT_DIR, "data", "student_data2.csv")
PLOTS_DIR = os.path.join(BASE_OUTPUT_DIR, "plots")
OUTPUTS_DIR = os.path.join(BASE_OUTPUT_DIR, "outputs")

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

sns.set_style("whitegrid")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ File not found: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    subjects = ['Math', 'Science', 'English']
    df['Average_Score'] = df[subjects].mean(axis=1)

    def assign_grade(score):
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        else:
            return 'D'

    df['Grade'] = df['Average_Score'].apply(assign_grade)

    df['Attendance_Level'] = pd.cut(
        df['Attendance'].clip(0, 100),
        bins=[0, 80, 90, 100],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )

    return df

df = load_data()
subjects = ['Math', 'Science', 'English']

# =========================
# TITLE
# =========================
st.title("📊 Student Performance Analysis Dashboard")
st.markdown("Comprehensive academic and attendance analysis")

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔍 Filters")

selected_subject = st.sidebar.selectbox(
    "Select Subject",
    subjects + ["Average_Score"]
)

selected_grades = st.sidebar.multiselect(
    "Select Grades",
    sorted(df['Grade'].unique()),
    default=sorted(df['Grade'].unique())
)

selected_attendance = st.sidebar.multiselect(
    "Attendance Level",
    df['Attendance_Level'].cat.categories,
    default=df['Attendance_Level'].cat.categories
)

filtered_df = df[
    (df['Grade'].isin(selected_grades)) &
    (df['Attendance_Level'].isin(selected_attendance))
]

if filtered_df.empty:
    st.warning("⚠️ No data matches selected filters")
    st.stop()

# =========================
# KPI METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", len(filtered_df))
col2.metric("Avg Score", f"{filtered_df['Average_Score'].mean():.2f}")
col3.metric("Avg Attendance", f"{filtered_df['Attendance'].mean():.1f}%")
col4.metric("Top Grade", filtered_df['Grade'].value_counts().idxmax())

# =========================
# DATA TABLE
# =========================
st.subheader("📋 Student Data")
st.dataframe(filtered_df, use_container_width=True)

# Download
st.download_button(
    "📥 Download CSV",
    filtered_df.to_csv(index=False).encode("utf-8"),
    "filtered_students.csv",
    "text/csv"
)

# =========================
# VISUALIZATIONS
# =========================
st.markdown("---")
st.header("📊 Visual Analysis")

# Histogram
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(filtered_df[selected_subject], bins=10, edgecolor="black")
ax.set_title(f"{selected_subject} Score Distribution")
ax.set_xlabel("Score")
ax.set_ylabel("Students")
st.pyplot(fig)
fig.savefig(os.path.join(PLOTS_DIR, f"hist_{selected_subject}.png"), dpi=300)
plt.close()

# Box Plot
fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(y=filtered_df[selected_subject], ax=ax)
ax.set_title(f"{selected_subject} Boxplot")
st.pyplot(fig)
fig.savefig(os.path.join(PLOTS_DIR, f"box_{selected_subject}.png"), dpi=300)
plt.close()

# Scatter Plot
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    x="Attendance",
    y="Average_Score",
    hue="Grade",
    data=filtered_df,
    s=80,
    ax=ax
)
ax.set_title("Attendance vs Average Score")
st.pyplot(fig)
fig.savefig(os.path.join(PLOTS_DIR, "scatter_attendance.png"), dpi=300)
plt.close()

# Violin Plot
fig, ax = plt.subplots(figsize=(8, 5))
sns.violinplot(data=filtered_df[subjects], ax=ax)
ax.set_title("Subject-wise Score Distribution")
st.pyplot(fig)
fig.savefig(os.path.join(PLOTS_DIR, "violin_subjects.png"), dpi=300)
plt.close()

# Heatmap
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    filtered_df[subjects + ['Attendance']].corr(),
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    ax=ax
)
ax.set_title("Correlation Heatmap")
st.pyplot(fig)
fig.savefig(os.path.join(PLOTS_DIR, "heatmap.png"), dpi=300)
plt.close()

# =========================
# SAVE OUTPUTS
# =========================
filtered_df.to_csv(
    os.path.join(OUTPUTS_DIR, "final_student_analysis.csv"),
    index=False
)

# =========================
# SAFE BACKUP
# =========================
try:
    import shutil
    shutil.copy(
        os.path.abspath(__file__),
        os.path.join(BASE_OUTPUT_DIR, "Student_data_backup.py")
    )
except NameError:
    pass

# =========================
# FOOTER
# =========================
st.success("✅ Analysis Complete")
st.info(f"📁 Plots saved in: {PLOTS_DIR}")
st.info(f"📁 Output saved in: {OUTPUTS_DIR}")
