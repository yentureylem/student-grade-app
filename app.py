import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")

# Upload files
exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    # Remove empty StudentID rows
    exam_df = exam_df[exam_df["StudentID"].notna()]
    seminar_df = seminar_df[seminar_df["StudentID"].notna()]

    # Rename grade columns
    exam_df = exam_df.rename(columns={"Rounded Grades": "Rounded Exam Grade"})
    seminar_df = seminar_df.rename(columns={"Rounded Grades": "Rounded Seminar Grade"})

    # Merge only on common StudentIDs
    merged_df = pd.merge(exam_df, seminar_df, on="StudentID", how="inner", suffixes=("_exam", "_seminar"))

    # Select name/email from exam file (you can change to seminar if needed)
    name_cols = ["First name_exam", "Last name_exam", "Email_exam"]
    for col in name_cols:
        if col not in merged_df.columns:
            merged_df[col] = ""

    # Calculate total grade
    merged_df["Total Grade"] = (
        0.7 * merged_df["Rounded Exam Grade"] +
        0.3 * merged_df["Rounded Seminar Grade"]
    ).round(2)

    # Final table
    final_df = merged_df[[
        "StudentID",
        "First name_exam",
        "Last name_exam",
        "Email_exam",
        "Rounded Exam Grade",
        "Rounded Seminar Grade",
        "Total Grade"
    ]].rename(columns={
        "First name_exam": "First name",
        "Last name_exam": "Last name",
        "Email_exam": "Email"
    })

    st.subheader("📌 Final Grades")
    st.dataframe(final_df)

    # Search by StudentID
    st.subheader("🔍 Search Student by ID")
    search_id = st.text_input("Enter StudentID to search:")
    if st.button("Search"):
        result_df = final_df[final_df["StudentID"].astype(str) == search_id.strip()]
        if not result_df.empty:
            st.write(result_df)
        else:
            st.error("❌ No student found with this ID.")

    # Download CSV
    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Final Grades (CSV)", data=csv, file_name="final_grades.csv", mime="text/csv")

else:
    st.info("Please upload both the exam and seminar CSV files to proceed.")
