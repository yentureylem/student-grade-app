import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("This application calculates students' final grades by combining exam (70%) and seminar (30%) grades using the 'Rounded Grades' columns.")

# Upload section
st.header("1️⃣ Upload Files")
exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    # Rename columns for clarity
    exam_df = exam_df.rename(columns={"Rounded Grades": "Rounded Exam Grade"})
    seminar_df = seminar_df.rename(columns={"Rounded Grades": "Rounded Seminar Grade"})

    # Merge on StudentID (inner join)
    merged_df = pd.merge(exam_df, seminar_df, on="StudentID", suffixes=("_exam", "_seminar"))

    # Calculate Total Grade
    merged_df["Total Grade"] = (0.7 * merged_df["Rounded Exam Grade"] +
                                0.3 * merged_df["Rounded Seminar Grade"])

    # Reorder columns for final table
    final_df = merged_df[[
        "StudentID",
        "First name",
        "Last name",
        "Email",
        "Rounded Exam Grade",
        "Rounded Seminar Grade",
        "Total Grade"
    ]]

    # Show Final Table
    st.subheader("📌 Final Grades")
    st.dataframe(final_df)

    # Search student by ID
    st.subheader("🔍 Search Student by ID")
    search_id = st.text_input("Enter StudentID to search:")
    if st.button("Search"):
        result_df = final_df[final_df["StudentID"].astype(str) == search_id.strip()]
        if not result_df.empty:
            st.write(result_df)
        else:
            st.error("❌ No student found with this ID.")

    # Download button
    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Final Grades (CSV)",
                       data=csv,
                       file_name="final_grades.csv",
                       mime="text/csv")
else:
    st.info("Please upload both the exam and seminar CSV files to proceed.")
