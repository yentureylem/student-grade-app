import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("Bu uygulama, öğrenci notlarını **%70 sınav + %30 seminer** ağırlıklarına göre hesaplar. Ayrıca ID numarasına göre arama yapılabilir.")

# 📂 Dosya yükleme
exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    st.success("✅ Dosyalar yüklendi!")

    # Ortak sütunlardan eşleştirme (StudentID veya ID Number)
    id_col = None
    for col in ["StudentID", "ID Number", "id", "ID"]:
        if col in exam_df.columns and col in seminar_df.columns:
            id_col = col
            break

    if id_col:
        merged_df = pd.merge(exam_df, seminar_df, on=id_col, how="outer")

        # Eğer ID numarası eksikse o öğrenciyi atla
        merged_df = merged_df[merged_df[id_col].notna()]

        # Sütun adlarını tespit et
        exam_col = [col for col in exam_df.columns if "grade" in col.lower() or "note" in col.lower()]
        seminar_col = [col for col in seminar_df.columns if "grade" in col.lower() or "note" in col.lower()]

        if exam_col and seminar_col:
            exam_col = exam_col[0]
            seminar_col = seminar_col[0]

            # Notları yuvarla ve toplam notu hesapla
            merged_df["Exam Grade"] = merged_df[exam_col].round()
            merged_df["Seminar Grade"] = merged_df[seminar_col].round()
            merged_df["Total Grade"] = (0.7 * merged_df["Exam Grade"] + 0.3 * merged_df["Seminar Grade"]).round(2)

            # Son tablo: ID, İsim, Mail, Notlar
            final_cols = [id_col, "First Name", "Last Name", "Email", "Exam Grade", "Seminar Grade", "Total Grade"]
            final_df = merged_df[final_cols] if all(col in merged_df.columns for col in final_cols) else merged_df

            st.subheader("📌 Final Grades")
            st.dataframe(final_df)

            # CSV olarak indirme
            csv = final_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Final Grades (CSV)", data=csv, file_name="final_grades.csv", mime="text/csv")

            # 🔍 ID ile arama
            search_id = st.text_input("🔍 Search by ID Number")
            if search_id:
                result_df = final_df[final_df[id_col].astype(str) == search_id]
                if not result_df.empty:
                    st.write("Arama Sonucu:")
                    st.dataframe(result_df)
                else:
                    st.warning("Bu ID numarasına ait öğrenci bulunamadı.")

        else:
            st.error("❌ Not sütunları bulunamadı. Lütfen dosyaları kontrol edin.")
    else:
        st.error("❌ Ortak ID sütunu bulunamadı.")
