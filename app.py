import streamlit as st
import pandas as pd

st.title("Student Grade Calculator")

# CSV dosyalarını yükleme
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    # CSV'leri oku
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

    # Eğer First Name, Last Name, E Mail boşsa diğer dosyadan doldur
    for col in ["First Name", "Last Name", "E Mail"]:
        merged[col] = merged[f"{col}_exam"].combine_first(merged[f"{col}_seminar"])

    # Toplam not hesaplama
    if "Rounded Exam Grades" in merged.columns and "Rounded Seminar Grades" in merged.columns:
        merged["Total Grade"] = (
            0.7 * merged["Rounded Exam Grades"] +
            0.3 * merged["Rounded Seminar Grades"]
        ).round(2)
    else:
        st.error("Lütfen dosyalarda 'Rounded Exam Grades' ve 'Rounded Seminar Grades' sütunları olduğundan emin olun.")

    # Final tablo
    final_df = merged[[
        "StudentID",
        "First Name",
        "Last Name",
        "E Mail",
        "Rounded Exam Grades",
        "Rounded Seminar Grades",
        "Total Grade"
    ]]

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
