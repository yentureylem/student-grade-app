import streamlit as st
import pandas as pd

st.title("Student Grade Calculator")

# CSV dosyalarını yükleme
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    try:
        # CSV'leri oku - index_col kullanma
        exam_df = pd.read_csv(exam_file)
        seminar_df = pd.read_csv(seminar_file)
        
        # Debug: Show file columns and sample data
        with st.expander("Debug: File Columns and Sample Data"):
            st.write("**Exam file columns:**")
            st.write(exam_df.columns.tolist())
            st.write("**Seminar file columns:**")
            st.write(seminar_df.columns.tolist())
            
            # Show first few rows to see actual data
            st.write("**First 3 rows of Exam file:**")
            st.dataframe(exam_df.head(3))
            st.write("**First 3 rows of Seminar file:**")
            st.dataframe(seminar_df.head(3))
        
        # Exam dosyasındaki boş sütunu kaldır ve sütun isimlerini düzelt
        if '' in exam_df.columns:
            exam_df = exam_df.drop(columns=[''])
        
        # Sütun isimlerini temizle (boşlukları kaldır)
        exam_df.columns = exam_df.columns.str.strip()
        seminar_df.columns = seminar_df.columns.str.strip()
        
        # Gerekli sütunları kontrol et
        required_cols_exam = ["StudentID", "Rounded Exam Grades", "First Name", "Last Name"]
        required_cols_seminar = ["StudentID", "Rounded Seminar Grades", "First Name", "Last Name"]
        
        # E Mail sütununu da kontrol et (opsiyonel)
        if "E Mail" in exam_df.columns:
            st.success("✅ E Mail column found in exam file")
        
        missing_exam = [col for col in required_cols_exam if col not in exam_df.columns]
        missing_seminar = [col for col in required_cols_seminar if col not in seminar_df.columns]
        
        if missing_exam or missing_seminar:
            st.error("Missing columns detected:")
            if missing_exam:
                st.error(f"Missing in exam file: {missing_exam}")
                st.write("Available columns in exam file:", exam_df.columns.tolist())
            if missing_seminar:
                st.error(f"Missing in seminar file: {missing_seminar}")
                st.write("Available columns in seminar file:", seminar_df.columns.tolist())
            st.stop()
        
        # StudentID sütununu temizle (boşlukları kaldır, string'e çevir)
        exam_df["StudentID"] = exam_df["StudentID"].astype(str).str.strip()
        seminar_df["StudentID"] = seminar_df["StudentID"].astype(str).str.strip()
        
        # NaN değerleri kontrol et ve temizle
        exam_df = exam_df.dropna(subset=["StudentID", "Rounded Exam Grades"])
        seminar_df = seminar_df.dropna(subset=["StudentID", "Rounded Seminar Grades"])
        
        # Debug: StudentID'leri kontrol et
        st.write("**StudentID Debug:**")
        st.write(f"Exam file StudentIDs count: {len(exam_df['StudentID'].unique())}")
        st.write(f"Seminar file StudentIDs count: {len(seminar_df['StudentID'].unique())}")
        
        # Common StudentID'leri bul
        common_ids = set(exam_df["StudentID"]).intersection(set(seminar_df["StudentID"]))
        st.write(f"Common StudentIDs: {len(common_ids)}")
        
        # Merge: StudentID üzerinden birleştirme (inner join)
        merged = pd.merge(
            exam_df,
            seminar_df,
            on="StudentID",
            suffixes=("_exam", "_seminar"),
            how="inner"
        )
        
        if merged.empty:
            st.error("No common StudentID found in both files. Please check your files.")
            st.stop()
        
        # İsim bilgilerini birleştir - öncelik exam dosyasında
        # First Name için
        if "First Name_exam" in merged.columns and "First Name_seminar" in merged.columns:
            merged["First Name"] = merged["First Name_exam"].fillna(merged["First Name_seminar"])
        elif "First Name_exam" in merged.columns:
            merged["First Name"] = merged["First Name_exam"]
        elif "First Name_seminar" in merged.columns:
            merged["First Name"] = merged["First Name_seminar"]
        else:
            merged["First Name"] = "N/A"
        
        # Last Name için
        if "Last Name_exam" in merged.columns and "Last Name_seminar" in merged.columns:
            merged["Last Name"] = merged["Last Name_exam"].fillna(merged["Last Name_seminar"])
        elif "Last Name_exam" in merged.columns:
            merged["Last Name"] = merged["Last Name_exam"]
        elif "Last Name_seminar" in merged.columns:
            merged["Last Name"] = merged["Last Name_seminar"]
        else:
            merged["Last Name"] = "N/A"
        
        # Email işlemi
        email_found = False
        if "E Mail" in exam_df.columns:
            if "E Mail_exam" in merged.columns:
                merged["E Mail"] = merged["E Mail_exam"]
                email_found = True
                st.success("📧 Email taken from exam file")
            elif "E Mail" in merged.columns:  # Suffix almamış durumda
                # E Mail sütunu zaten var, değiştirme
                email_found = True
                st.success("📧 Email column preserved")
        
        if not email_found:
            merged["E Mail"] = "N/A"
            st.warning("⚠️ No email column found")
        
        # Email temizleme - sadece @tu-ilmenau.de emaillerini tut
        if email_found and "E Mail" in merged.columns:
            merged["E Mail"] = merged["E Mail"].apply(
                lambda x: x if (pd.notna(x) and '@tu-ilmenau.de' in str(x)) else "N/A"
            )
            
            # İstatistikleri göster
            valid_emails = merged["E Mail"][merged["E Mail"] != "N/A"].count()
            total_students = len(merged)
            st.info(f"📊 Found {valid_emails} valid @tu-ilmenau.de emails out of {total_students} students")
        
        # Grade sütunlarını numeric'e çevir
        try:
            merged["Rounded Exam Grades"] = pd.to_numeric(merged["Rounded Exam Grades"], errors='coerce')
            merged["Rounded Seminar Grades"] = pd.to_numeric(merged["Rounded Seminar Grades"], errors='coerce')
        except Exception as e:
            st.error(f"Could not convert grade values to numeric format: {e}")
            st.stop()
        
        # NaN değerleri kontrol et
        nan_exam = merged["Rounded Exam Grades"].isna().sum()
        nan_seminar = merged["Rounded Seminar Grades"].isna().sum()
        
        if nan_exam > 0 or nan_seminar > 0:
            st.warning(f"Warning: {nan_exam} exam grades and {nan_seminar} seminar grades are missing/invalid")
        
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
        
        # Mevcut sütunları al
        available_columns = [col for col in final_columns if col in merged.columns]
        final_df = merged[available_columns].copy()
        
        # Sütun isimlerini yeniden adlandır
        final_df = final_df.rename(columns={
            "StudentID": "ID Number",
            "Rounded Exam Grades": "Exam Grade",
            "Rounded Seminar Grades": "Seminar Grade"
        })
        
        # Sonuçları göster
        st.success(f"✅ {len(final_df)} students processed successfully")
        
        # İstatistikler
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Students", len(final_df))
        with col2:
            st.metric("Average Grade", f"{final_df['Total Grade'].mean():.2f}")
        with col3:
            st.metric("Lowest Grade", f"{final_df['Total Grade'].min():.2f}")
        
        # Final tablo
        st.subheader("📊 Final Table")
        st.dataframe(final_df, use_container_width=True)
        
        # CSV download seçeneği
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Final Table as CSV",
            data=csv,
            file_name="final_grades.csv",
            mime="text/csv"
        )
        
        # Öğrenci arama
        st.subheader("🔍 Student Search")
        search_id = st.text_input("Enter StudentID:")
        
        if search_id:
            # Arama yap
            result = final_df[final_df["ID Number"].astype(str).str.contains(search_id.strip(), case=False, na=False)]
            
            if not result.empty:
                st.success(f"🎯 {len(result)} student(s) found:")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("❌ No student found with this ID.")
        
        # Not dağılımı grafiği
        st.subheader("📈 Grade Distribution")
        if len(final_df) > 0:
            # Histogram verisi oluştur
            import numpy as np
            grades = final_df['Total Grade'].dropna()
            
            # Bin'leri hesapla
            min_grade = grades.min()
            max_grade = grades.max()
            bins = np.linspace(min_grade, max_grade, 21)  # 20 bins
            hist, bin_edges = np.histogram(grades, bins=bins)
            
            # Streamlit için histogram chart verisi oluştur
            chart_data = []
            for i in range(len(hist)):
                bin_center = (bin_edges[i] + bin_edges[i+1]) / 2
                chart_data.append({
                    'Grade Range': f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}",
                    'Grade': bin_center,
                    'Count': hist[i]
                })
            
            hist_df = pd.DataFrame(chart_data)
            
            # Bar chart göster
            st.bar_chart(data=hist_df.set_index('Grade')['Count'])
            
            # İstatistik tablosu
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Grade Statistics:**")
                stats_df = pd.DataFrame({
                    'Statistic': ['Minimum', 'Maximum', 'Mean', 'Median', 'Std Dev'],
                    'Value': [
                        f"{grades.min():.2f}",
                        f"{grades.max():.2f}",
                        f"{grades.mean():.2f}",
                        f"{grades.median():.2f}",
                        f"{grades.std():.2f}"
                    ]
                })
                st.dataframe(stats_df, use_container_width=True)
            
            with col2:
                st.write("**Grade Ranges:**")
                # Not aralıkları oluştur
                grade_ranges = [
                    ('A (90-100)', len(grades[(grades >= 90) & (grades <= 100)])),
                    ('B (80-89)', len(grades[(grades >= 80) & (grades < 90)])),
                    ('C (70-79)', len(grades[(grades >= 70) & (grades < 80)])),
                    ('D (60-69)', len(grades[(grades >= 60) & (grades < 70)])),
                    ('F (0-59)', len(grades[grades < 60]))
                ]
                
                ranges_df = pd.DataFrame(grade_ranges, columns=['Grade', 'Count'])
                st.dataframe(ranges_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.error("Please check the format of your files.")
        
        # Hata detayları
        with st.expander("Error Details"):
            st.exception(e)

else:
    st.info("👆 Please upload both Exam and Seminar CSV files.")
