import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grade Calculator", layout="wide")

st.title("🎓 Student Grade Calculator")
st.markdown("This app calculates students' final grades using 70% exam and 30% seminar **rounded grades**.")

st.header("1️⃣ Upload Files")
exam_file = st.file_uploader("📄 Upload Exam Grades CSV File", type=["csv"], key="exam")
seminar_file = st.file_uploader("📄 Upload Seminar Grades CSV File", type=["csv"], key="seminar")

if exam_file and seminar_file:
    exam_df = pd.read_csv(exam_file)
    seminar_df = pd.read_csv(seminar_file)

    st.success("✅ Both files uploaded successfully!")

    # Ortak kolon ismini bul
    possible_id_cols = ["StudentID", "ID number", "ID", "id", "Id Number"]
    common_id_col = None
    for col in possible_id_cols:
        if col in exam_df.columns and col in seminar_df.columns:
            common_id_col = col
            break

    if not common_id_col:
        st.error("❌ Ortak bir ID kolonu bulunamadı. Lütfen dosyaları kontrol edin.")
    else:
        # Merge işlemi
        merged_df = pd.merge(exam_df, seminar_df, on=common_id_col, how="inner")

        # "Rounded Grades" kolonlarını bul
        exam_round_col = [col for col in exam_df.columns if "Rounded" in col or "rounded" in col][0]
        seminar_round_col = [col for col in seminar_df.columns if "Rounded" in col or "rounded" in col][0]

        # Final Grade hesaplama
        merged_df["Final Grade"] = (0.7 * merged_df[exam_round_col] +
                                    0.3 * merged_df[seminar_round_col]).round(2)

        # Arama özelliği
        st.subheader("🔍 Search Student by ID")
        search_id = st.text_input("Enter StudentID to search:")
        if search_id:
            result = merged_df[merged_df[common_id_col].astype(str) == str(search_id)]
            if not result.empty:
                display_cols = [common_id_col, "First Name_x", "Last Name_x", "Email_x",
                                exam_round_col, seminar_round_col, "Final Grade"]
                st.dataframe(result[display_cols])
            else:
                st.warning("No student found with this ID.")

        # Final tabloyu göster
        st.subheader("📌 Final Grades Table")
        display_cols = [common_id_col, "First Name_x", "Last Name_x", "Email_x",
                        exam_round_col, seminar_round_col, "Final Grade"]
        st.dataframe(merged_df[display_cols])

        # CSV olarak indir
        csv = merged_df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Final Grades (CSV)", data=csv,
                           file_name="final_grades.csv", mime="text/csv")
