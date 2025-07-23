import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("This application calculates students' final grades by combining exam (25%) and seminar (75%) grades.")

st.header("1️⃣ Upload Files")

exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    st.success("✅ Both file has been uploaded successfully!")

    st.subheader("📊 Exam Grades")
    st.dataframe(exam_df.head())

    st.subheader("📊 Seminar Grades")
    st.dataframe(seminar_df.head())

    common_cols = list(set(exam_df.columns).intersection(set(seminar_df.columns)))
    if "StudentID" in common_cols:
        merged_df = pd.merge(exam_df, seminar_df, on="StudentID")

        st.subheader("🔗 Combined Data")
        st.dataframe(merged_df.head())

        exam_col = [col for col in exam_df.columns if "grade" in col.lower() or "note" in col.lower()][0]
        seminar_col = [col for col in seminar_df.columns if "grade" in col.lower() or "note" in col.lower()][0]

        merged_df["Final Grade"] = 0.25 * merged_df[exam_col] + 0.75 * merged_df[seminar_col]

        st.subheader("📌 Final Grades")
        st.dataframe(merged_df[["StudentID", exam_col, seminar_col, "Final Grade"]])

        csv = merged_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Final Grades (CSV)", data=csv, file_name="final_grades.csv", mime="text/csv")

    else:
        st.error("❌ 'StudentID' ortak sütun olarak bulunamadı. Lütfen dosyaları kontrol edin.")
