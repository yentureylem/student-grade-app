import streamlit as st
import pandas as pd

st.title("Student Grades App")

# Dosyaları yükle
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    sem_df = pd.read_csv(seminar_file)

    # Merge
    merged = pd.merge(exam_df, sem_df, on="StudentID", how="inner", suffixes=("_exam", "_seminar"))

    # Eksik isim/email doldurma
    for col in ["First Name", "Last Name", "E Mail"]:
        exam_col = f"{col}_exam" if f"{col}_exam" in merged.columns else col
        seminar_col = f"{col}_seminar" if f"{col}_seminar" in merged.columns else col
        merged[col] = merged.get(exam_col).combine_first(merged.get(seminar_col))

    # Hesaplama (Rounded Grades üzerinden)
    exam_round_col = "Rounded Grade_exam" if "Rounded Grade_exam" in merged.columns else "Rounded Grade_x"
    seminar_round_col = "Rounded Grade_seminar" if "Rounded Grade_seminar" in merged.columns else "Rounded Grade_y"

    merged["Total Grade"] = (0.7 * merged[exam_round_col] + 0.3 * merged[seminar_round_col]).round(2)

    # Final tablo
    final_df = merged[[
        "StudentID",
        "First Name",
        "Last Name",
        "E Mail",
        exam_round_col,
        seminar_round_col,
        "Total Grade"
    ]].rename(columns={
        exam_round_col: "Rounded Exam Grade",
        seminar_round_col: "Rounded Seminar Grade"
    })

    st.subheader("Final Grades Table")
    st.dataframe(final_df)

    # Search by StudentID
    st.subheader("Search for a Student")
    search_id = st.text_input("Enter StudentID")
    if st.button("Search"):
        result = final_df[final_df["StudentID"].astype(str) == str(search_id)]
        if not result.empty:
            st.write(result)
        else:
            st.warning("No student found with this ID.")
