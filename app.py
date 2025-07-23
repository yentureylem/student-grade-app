import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("Bu uygulama, exam (%25) ve seminar (%75) notlarını birleştirerek öğrencilerin final notlarını hesaplar.")

st.header("1️⃣ Dosyaları Yükle")

exam_file = st.file_uploader("📄 Exam Grades CSV Dosyasını Yükleyin", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Seminar Grades CSV Dosyasını Yükleyin", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    st.success("✅ Her iki dosya başarıyla yüklendi!")

    st.subheader("📊 Exam Grades")
    st.dataframe(exam_df.head())

    st.subheader("📊 Seminar Grades")
    st.dataframe(seminar_df.head())

    common_cols = list(set(exam_df.columns).intersection(set(seminar_df.columns)))
    if "StudentID" in common_cols:
        merged_df = pd.merge(exam_df, seminar_df, on="StudentID")

        st.subheader("🔗 Birleştirilmiş Veriler")
        st.dataframe(merged_df.head())

        exam_col = [col for col in exam_df.columns if "grade" in col.lower() or "note" in col.lower()][0]
        seminar_col = [col for col in seminar_df.columns if "grade" in col.lower() or "note" in col.lower()][0]

        merged_df["Final Grade"] = 0.25 * merged_df[exam_col] + 0.75 * merged_df[seminar_col]

        st.subheader("📌 Final Notları")
        st.dataframe(merged_df[["StudentID", exam_col, seminar_col, "Final Grade"]])

        csv = merged_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Final Notlarını İndir (CSV)", data=csv, file_name="final_grades.csv", mime="text/csv")

    else:
        st.error("❌ 'StudentID' ortak sütun olarak bulunamadı. Lütfen dosyaları kontrol edin.")
