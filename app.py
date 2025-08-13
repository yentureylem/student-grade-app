import streamlit as st
import pandas as pd

st.title("Student Grade Calculator")

# CSV dosyalarını yükleme
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    # CSV dosyalarını oku
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    # Merge: StudentID üzerinden birleştirme
    merged = pd.merge(
        exam_df,
        seminar_df,
        on="StudentID",
        suffixes=("_exam", "_seminar"),
        how="outer"
    )

    # Rounded Grades sütunları
    exam_round_col = "Rounded Grades_exam"
    seminar_round_col = "Rounded Grades_seminar"

    if exam_round_col in merged.columns and seminar_round_col in merged.columns:
        merged["Total Grade"] = (
            0.7 * merged[exam_round_col] +
            0.3 * merged[seminar_round_col]
        ).round(2)
    else:
        st.error("Rounded Grades sütunları bulunamadı. Lütfen dosyaları kontrol edin.")

    # Final tablo: gerekli sütunlar
    final_df = merged[[
        "StudentID",
        "First Name_exam",
        "Last Name_exam",
        "E Mail_exam",
        exam_round_col,
        seminar_round_col,
        "Total Grade"
    ]].rename(columns={
        "First Name_exam": "First Name",
        "Last Name_exam": "Last Name",
        "E Mail_exam": "E Mail",
        exam_round_col: "Exam Rounded Grade",
        seminar_round_col: "Seminar Rounded Grade"
    })

    st.subheader("Final Table")
    st.dataframe(final_df)

    # Search by StudentID
    search_id = st.text_input("Search for StudentID")
    if st.button("Search"):
        result = final_df[final_df["StudentID"].astype(str) == search_id.strip()]
        if not result.empty:
            st.write("Student Found:")
            st.dataframe(result)
        else:
            st.warning("No student found with this ID.")
