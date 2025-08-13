import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")
st.title("🎓 Student Grade Calculator")

st.markdown("Final grade = **70% Exam (Rounded)** + **30% Seminar (Rounded)**")

# ---- Helper: ID normalize ----
def normalize_id(df):
    df = df.copy()
    df["StudentID"] = df["StudentID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    df = df[df["StudentID"].ne("") & df["StudentID"].notna()]
    return df

# ---- Upload ----
st.header("1️⃣ Upload Files")
exam_file = st.file_uploader("📄 Upload Exam Grades CSV", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV", type=["csv"], key="seminar")

if not (exam_file and seminar_file):
    st.info("Both CSVs required.")
    st.stop()

exam_df = pd.read_csv(exam_file)
sem_df = pd.read_csv(seminar_file)

# normalize IDs
exam_df = normalize_id(exam_df)
sem_df = normalize_id(sem_df)

# ---- Merge ----
merged = pd.merge(exam_df, sem_df, on="StudentID", how="inner", suffixes=("_exam", "_seminar"))

# isim ve e-posta doldurma (boşsa diğer dosyadan al)
for col in ["First Name", "Last Name", "E Mail"]:
    merged[col] = merged[f"{col}_exam"].combine_first(merged[f"{col}_seminar"])

# ---- Rounded columns ----
exam_round = "Rounded Exam Grade"
seminar_round = "Rounded Seminar Grade"

# varsa orijinal kolon adlarını bul
for c in merged.columns:
    if "rounded" in c.lower() and "exam" in c.lower():
        exam_round = c
    if "rounded" in c.lower() and "seminar" in c.lower():
        seminar_round = c

# ---- Final calculation ----
merged["Rounded Exam Grade"] = pd.to_numeric(merged[exam_round], errors="coerce")
merged["Rounded Seminar Grade"] = pd.to_numeric(merged[seminar_round], errors="coerce")
merged["Total Grade"] = (0.7 * merged["Rounded Exam Grade"] + 0.3 * merged["Rounded Seminar Grade"]).round(2)

final_df = merged[[
    "StudentID", "First Name", "Last Name", "E Mail",
    "Rounded Exam Grade", "Rounded Seminar Grade", "Total Grade"
]]

st.subheader("📌 Final Table")
st.dataframe(final_df, use_container_width=True)

# ---- Search Form ----
st.subheader("🔍 Search by StudentID")
with st.form("search_form", clear_on_submit=False):
    q = st.text_input("Enter StudentID")
    submitted = st.form_submit_button("Search")
    if submitted:
        q_norm = str(q).strip().replace(".0", "")
        found = final_df[final_df["StudentID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True) == q_norm]
        if found.empty:
            st.warning("No student found with this ID.")
        else:
            st.dataframe(found, use_container_width=True)

# ---- Download ----
csv = final_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Final Grades (CSV)",
    data=csv,
    file_name="final_grades.csv",
    mime="text/csv"
)
