import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("This app calculates students' final grades using 70% exam and 30% seminar **rounded grades**.")

# Upload files
exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    # Find common ID column
    possible_id_cols = ["StudentID", "ID number", "ID", "id", "Id Number"]
    common_id_col = None
    for col in possible_id_cols:
        if col in exam_df.columns and col in seminar_df.columns:
            common_id_col = col
            break

    if not common_id_col:
        st.error("❌ No common ID column found.")
    else:
        # Merge
        merged_df = pd.merge(exam_df, seminar_df, on=common_id_col, how="inner")

        # Find Rounded Grade columns in merged file
        exam_round_col = [col for col in merged_df.columns if "Rounded" in col and col.endswith("_x")][0]
        seminar_round_col = [col for col in merged_df.columns if "Rounded" in col and col.endswith("_y")][0]

        # Calculate final grade
        merged_df["Final Grade"] = (
            0.7 * merged_df[exam_round_col] +
            0.3 * merged_df[seminar_round_col]
        ).round(2)

        # Search
        st.subheader("🔍 Search Student by ID")
        search_id = st.text_input("Enter StudentID to search:")
        if search_id:
            result = merged_df[merged_df[common_id_col].astype(str) == str(search_id)]
            if not result.empty:
                st.dataframe(result)
            else:
                st.warning("No student found with this ID.")

        # Show final table
        st.subheader("📌 Final Grades Table")
        st.dataframe(merged_df[[common_id_col, exam_round_col, seminar_round_col, "Final Grade"]])

        # Download
        csv = merged_df[[common_id_col, exam_round_col, seminar_round_col, "Final Grade"]].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Final Grades (CSV)", data=csv, file_name="final_grades.csv", mime="text/csv")
