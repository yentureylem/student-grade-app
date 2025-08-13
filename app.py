import streamlit as st
import pandas as pd

st.title("Student Grade Calculator")

# CSV dosyalarını yükleme
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    try:
        # CSV'leri oku
        exam_df = pd.read_csv(exam_file)
        seminar_df = pd.read_csv(seminar_file)
        
        # Debug: Dosyaların sütunlarını göster
        with st.expander("Debug: Dosya Sütunları"):
            st.write("**Exam dosyası sütunları:**")
            st.write(exam_df.columns.tolist())
            st.write("**Seminar dosyası sütunları:**")
            st.write(seminar_df.columns.tolist())
        
        # Gerekli sütunları kontrol et
        required_cols_exam = ["StudentID", "Rounded Exam Grades"]
        required_cols_seminar = ["StudentID", "Rounded Seminar Grades"]
        
        missing_exam = [col for col in required_cols_exam if col not in exam_df.columns]
        missing_seminar = [col for col in required_cols_seminar if col not in seminar_df.columns]
        
        if missing_exam or missing_seminar:
            st.error("Eksik sütunlar tespit edildi:")
            if missing_exam:
                st.error(f"Exam dosyasında eksik: {missing_exam}")
            if missing_seminar:
                st.error(f"Seminar dosyasında eksik: {missing_seminar}")
            st.stop()
        
        # StudentID sütununu temizle (boşlukları kaldır, string'e çevir)
        exam_df["StudentID"] = exam_df["StudentID"].astype(str).str.strip()
        seminar_df["StudentID"] = seminar_df["StudentID"].astype(str).str.strip()
        
        # NaN değerleri kontrol et ve temizle
        exam_df = exam_df.dropna(subset=["StudentID", "Rounded Exam Grades"])
        seminar_df = seminar_df.dropna(subset=["StudentID", "Rounded Seminar Grades"])
        
        # Merge: StudentID üzerinden birleştirme (inner join kullan - her iki dosyada da olan öğrenciler)
        merged = pd.merge(
            exam_df,
            seminar_df,
            on="StudentID",
            suffixes=("_exam", "_seminar"),
            how="inner"  # outer yerine inner kullan
        )
        
        if merged.empty:
            st.error("İki dosyada ortak StudentID bulunamadı. Lütfen dosyalarınızı kontrol edin.")
            st.stop()
        
        # Kişisel bilgileri birleştir (önce exam'den al, yoksa seminar'den)
        info_cols = ["First Name", "Last Name", "E Mail"]
        for col in info_cols:
            if f"{col}_exam" in merged.columns and f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_exam"].combine_first(merged[f"{col}_seminar"])
            elif f"{col}_exam" in merged.columns:
                merged[col] = merged[f"{col}_exam"]
            elif f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_seminar"]
            else:
                merged[col] = "N/A"  # Hiçbiri yoksa N/A koy
        
        # Numeric sütunları kontrol et ve dönüştür
        try:
            merged["Rounded Exam Grades"] = pd.to_numeric(merged["Rounded Exam Grades"], errors='coerce')
            merged["Rounded Seminar Grades"] = pd.to_numeric(merged["Rounded Seminar Grades"], errors='coerce')
        except Exception as e:
            st.error(f"Not değerleri sayısal formata çevrilemedi: {e}")
            st.stop()
        
        # NaN değerlerini kontrol et
        nan_exam = merged["Rounded Exam Grades"].isna().sum()
        nan_seminar = merged["Rounded Seminar Grades"].isna().sum()
        
        if nan_exam > 0 or nan_seminar > 0:
            st.warning(f"Uyarı: {nan_exam} exam notu ve {nan_seminar} seminer notu eksik/geçersiz")
        
        # Toplam not hesaplama (70% exam + 30% seminar)
        merged["Total Grade"] = (
            0.7 * merged["Rounded Exam Grades"] + 
            0.3 * merged["Rounded Seminar Grades"]
        ).round(2)
        
        # Final tabloyu oluştur
        final_columns = [
            "StudentID",
            "First Name", 
            "Last Name",
            "E Mail",
            "Rounded Exam Grades",
            "Rounded Seminar Grades", 
            "Total Grade"
        ]
        
        # Sadece mevcut sütunları al
        available_columns = [col for col in final_columns if col in merged.columns]
        final_df = merged[available_columns].copy()
        
        # Sütun isimlerini düzenle
        final_df = final_df.rename(columns={
            "StudentID": "ID Number",
            "Rounded Exam Grades": "Exam Grade",
            "Rounded Seminar Grades": "Seminar Grade"
        })
        
        # Sonuçları göster
        st.success(f"✅ {len(final_df)} öğrenci başarıyla işlendi")
        
        # İstatistikler
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Toplam Öğrenci", len(final_df))
        with col2:
            st.metric("Ortalama Not", f"{final_df['Total Grade'].mean():.2f}")
        with col3:
            st.metric("En Yüksek Not", f"{final_df['Total Grade'].max():.2f}")
        
        # Final tablo
        st.subheader("📊 Final Table")
        st.dataframe(final_df, use_container_width=True)
        
        # CSV indirme seçeneği
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="📥 Final Tabloyu CSV olarak İndir",
            data=csv,
            file_name="final_grades.csv",
            mime="text/csv"
        )
        
        # Öğrenci arama
        st.subheader("🔍 Öğrenci Arama")
        search_id = st.text_input("StudentID girin:")
        
        if search_id:
            # Arama yap
            result = final_df[final_df["ID Number"].astype(str).str.contains(search_id.strip(), case=False, na=False)]
            
            if not result.empty:
                st.success(f"🎯 {len(result)} öğrenci bulundu:")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("❌ Bu ID ile öğrenci bulunamadı.")
        
        # Not dağılımı grafiği
        st.subheader("📈 Not Dağılımı")
        if len(final_df) > 0:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.hist(final_df['Total Grade'], bins=20, edgecolor='black', alpha=0.7)
            ax.set_xlabel('Total Grade')
            ax.set_ylabel('Frequency')
            ax.set_title('Grade Distribution')
            st.pyplot(fig)
        
    except Exception as e:
        st.error(f"❌ Bir hata oluştu: {str(e)}")
        st.error("Lütfen dosyalarınızın formatını kontrol edin.")
        
        # Hata detayları
        with st.expander("Hata Detayları"):
            st.exception(e)

else:
    st.info("👆 Lütfen hem Exam hem de Seminar CSV dosyalarını yükleyin.")
