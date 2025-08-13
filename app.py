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
        
        # Debug: Show file columns
        with st.expander("Debug: File Columns"):
            st.write("**Exam file columns:**")
            st.write(exam_df.columns.tolist())
            st.write("**Seminar file columns:**")
            st.write(seminar_df.columns.tolist())
        
        # Gerekli sütunları kontrol et
        required_cols_exam = ["StudentID", "Rounded Exam Grades"]
        required_cols_seminar = ["StudentID", "Rounded Seminar Grades"]
        
        missing_exam = [col for col in required_cols_exam if col not in exam_df.columns]
        missing_seminar = [col for col in required_cols_seminar if col not in seminar_df.columns]
        
        if missing_exam or missing_seminar:
            st.error("Missing columns detected:")
            if missing_exam:
                st.error(f"Missing in exam file: {missing_exam}")
            if missing_seminar:
                st.error(f"Missing in seminar file: {missing_seminar}")
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
            st.error("No common StudentID found in both files. Please check your files.")
            st.stop()
        
        # Combine personal information (prioritize exam file, fallback to seminar file)
        info_cols = ["First Name", "Last Name", "E Mail", "Email", "E-Mail", "E-mail", "email"]
        
        # Create a mapping for email columns
        email_col = None
        for col in info_cols[3:]:  # Check email variations
            if col in exam_df.columns:
                email_col = col
                break
            elif col in seminar_df.columns:
                email_col = col
                break
        
        # Process basic info columns
        for col in ["First Name", "Last Name"]:
            if f"{col}_exam" in merged.columns and f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_exam"].combine_first(merged[f"{col}_seminar"])
            elif f"{col}_exam" in merged.columns:
                merged[col] = merged[f"{col}_exam"]
            elif f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_seminar"]
            else:
                merged[col] = "N/A"
        
        # Handle email column specifically
        if email_col:
            if f"{email_col}_exam" in merged.columns and f"{email_col}_seminar" in merged.columns:
                merged["E Mail"] = merged[f"{email_col}_exam"].combine_first(merged[f"{email_col}_seminar"])
            elif f"{email_col}_exam" in merged.columns:
                merged["E Mail"] = merged[f"{email_col}_exam"]
            elif f"{email_col}_seminar" in merged.columns:
                merged["E Mail"] = merged[f"{email_col}_seminar"]
            else:
                merged["E Mail"] = "N/A"
        else:
            merged["E Mail"] = "N/A"
        
        # Convert to numeric and check
        try:
            merged["Rounded Exam Grades"] = pd.to_numeric(merged["Rounded Exam Grades"], errors='coerce')
            merged["Rounded Seminar Grades"] = pd.to_numeric(merged["Rounded Seminar Grades"], errors='coerce')
        except Exception as e:
            st.error(f"Could not convert grade values to numeric format: {e}")
            st.stop()
        
        # Check for NaN values
        nan_exam = merged["Rounded Exam Grades"].isna().sum()
        nan_seminar = merged["Rounded Seminar Grades"].isna().sum()
        
        if nan_exam > 0 or nan_seminar > 0:
            st.warning(f"Warning: {nan_exam} exam grades and {nan_seminar} seminar grades are missing/invalid")
        
        # Toplam not hesaplama (70% exam + 30% seminar)
        merged["Total Grade"] = (
            0.7 * merged["Rounded Exam Grades"] + 
            0.3 * merged["Rounded Seminar Grades"]
        ).round(2)
        
        # Create final table
        final_columns = [
            "StudentID",
            "First Name", 
            "Last Name",
            "E Mail",
            "Rounded Exam Grades",
            "Rounded Seminar Grades", 
            "Total Grade"
        ]
        
        # Get only available columns
        available_columns = [col for col in final_columns if col in merged.columns]
        final_df = merged[available_columns].copy()
        
        # Rename columns
        final_df = final_df.rename(columns={
            "StudentID": "ID Number",
            "Rounded Exam Grades": "Exam Grade",
            "Rounded Seminar Grades": "Seminar Grade"
        })
        
        # Show results
        st.success(f"✅ {len(final_df)} students processed successfully")
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Students", len(final_df))
        with col2:
            st.metric("Average Grade", f"{final_df['Total Grade'].mean():.2f}")
        with col3:
            st.metric("Highest Grade", f"{final_df['Total Grade'].min():.2f}")
        
        # Final tablo
        st.subheader("📊 Final Table")
        st.dataframe(final_df, use_container_width=True)
        
        # CSV download option
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Final Table as CSV",
            data=csv,
            file_name="final_grades.csv",
            mime="text/csv"
        )
        
        # Student search
        st.subheader("🔍 Student Search")
        search_id = st.text_input("Enter StudentID:")
        
        if search_id:
            # Search
            result = final_df[final_df["ID Number"].astype(str).str.contains(search_id.strip(), case=False, na=False)]
            
            if not result.empty:
                st.success(f"🎯 {len(result)} student(s) found:")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("❌ No student found with this ID.")
        
        # Grade distribution chart
        st.subheader("📈 Grade Distribution")
        if len(final_df) > 0:
            # Create histogram data
            import numpy as np
            grades = final_df['Total Grade'].dropna()
            
            # Calculate bins
            min_grade = grades.min()
            max_grade = grades.max()
            bins = np.linspace(min_grade, max_grade, 21)  # 20 bins
            hist, bin_edges = np.histogram(grades, bins=bins)
            
            # Create histogram chart data for Streamlit
            chart_data = []
            for i in range(len(hist)):
                bin_center = (bin_edges[i] + bin_edges[i+1]) / 2
                chart_data.append({
                    'Grade Range': f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}",
                    'Grade': bin_center,
                    'Count': hist[i]
                })
            
            hist_df = pd.DataFrame(chart_data)
            
            # Display bar chart
            st.bar_chart(data=hist_df.set_index('Grade')['Count'])
            
            # Statistics table
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
                # Create grade ranges
                grade_ranges = [
                    ('A (0.0-1.0)', len(grades[(grades >= 1.0) & (grades <= 0.0)])),
                    ('B (1.0-2.0)', len(grades[(grades >= 2.0) & (grades < 1.0)])),
                    ('C (2.0-3.0)', len(grades[(grades >= 3.0) & (grades < 2.0)])),
                    ('D (3.0-4.0)', len(grades[(grades >= 4.0) & (grades < 3.0)])),
                    ('F (5.0)', len(grades[grades < 4.0]))
                ]
                
                ranges_df = pd.DataFrame(grade_ranges, columns=['Grade', 'Count'])
                st.dataframe(ranges_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.error("Please check the format of your files.")
        
        # Error details
        with st.expander("Error Details"):
            st.exception(e)

else:
    st.info("👆 Please upload both Exam and Seminar CSV files.")
