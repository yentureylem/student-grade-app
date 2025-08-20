import streamlit as st
import pandas as pd

st.title("Student Grade Calculator")

# CSV dosyalarını yükleme
exam_file = st.file_uploader("Upload Exam Grades CSV", type=["csv"])
seminar_file = st.file_uploader("Upload Seminar Grades CSV", type=["csv"])

if exam_file and seminar_file:
    try:
        # CSV'leri oku - ilk sütun index olarak kullan
        exam_df = pd.read_csv(exam_file, index_col=0)
        seminar_df = pd.read_csv(seminar_file, index_col=0)
        
        # Reset index to make sure StudentID is accessible
        exam_df = exam_df.reset_index(drop=True)
        seminar_df = seminar_df.reset_index(drop=True)
        
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
            
            # Check for email columns specifically
            st.write("**Email column detection:**")
            email_variations = ["E Mail", "Email", "E-Mail", "E-mail", "email", "EMAIL", "e-mail", "e_mail", "E_Mail"]
            found_emails = []
            for var in email_variations:
                if var in exam_df.columns:
                    # Show sample data from this column
                    sample_data = exam_df[var].dropna().head(3).tolist()
                    found_emails.append(f"'{var}' found in EXAM file - Sample: {sample_data}")
                if var in seminar_df.columns:
                    sample_data = seminar_df[var].dropna().head(3).tolist()
                    found_emails.append(f"'{var}' found in SEMINAR file - Sample: {sample_data}")
            
            if found_emails:
                for email_info in found_emails:
                    st.write(f"✅ {email_info}")
            else:
                st.write("❌ No standard email columns found")
                
                # Search for columns containing @tu-ilmenau.de
                st.write("**Searching for @tu-ilmenau.de in all columns:**")
                tu_email_found = False
                for col in exam_df.columns:
                    if exam_df[col].dtype == 'object':  # Only check text columns
                        tu_emails = exam_df[col].astype(str).str.contains('@tu-ilmenau.de', na=False)
                        if tu_emails.any():
                            sample_emails = exam_df[col][tu_emails].head(3).tolist()
                            st.write(f"✅ Found @tu-ilmenau.de emails in EXAM column '{col}': {sample_emails}")
                            tu_email_found = True
                
                for col in seminar_df.columns:
                    if seminar_df[col].dtype == 'object':
                        tu_emails = seminar_df[col].astype(str).str.contains('@tu-ilmenau.de', na=False)
                        if tu_emails.any():
                            sample_emails = seminar_df[col][tu_emails].head(3).tolist()
                            st.write(f"✅ Found @tu-ilmenau.de emails in SEMINAR column '{col}': {sample_emails}")
                            tu_email_found = True
                            
                if not tu_email_found:
                    st.write("❌ No @tu-ilmenau.de emails found in any column")
        
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
        
        # Combine personal information (prioritize exam file)
        # Handle basic info columns
        for col in ["First Name", "Last Name"]:
            if f"{col}_exam" in merged.columns and f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_exam"].combine_first(merged[f"{col}_seminar"])
            elif f"{col}_exam" in merged.columns:
                merged[col] = merged[f"{col}_exam"]
            elif f"{col}_seminar" in merged.columns:
                merged[col] = merged[f"{col}_seminar"]
            else:
                merged[col] = "N/A"
        
        # Handle email column - E Mail sütunu direkt exam dosyasından alınacak
        email_found = False
        
        # E Mail sütunu varsa direkt kullan
        if "E Mail" in merged.columns and "E Mail" not in [f"E Mail_exam", f"E Mail_seminar"]:
            # Bu durumda merge işlemi sütunu _exam _seminar eki olmadan bırakmış
            merged["Email_Final"] = merged["E Mail"]
            email_found = True
            st.success("📧 Email taken from 'E Mail' column")
        elif "E Mail_exam" in merged.columns:
            merged["Email_Final"] = merged["E Mail_exam"] 
            email_found = True
            st.success("📧 Email taken from exam file 'E Mail' column")
        elif "E Mail_seminar" in merged.columns:
            merged["Email_Final"] = merged["E Mail_seminar"]
            email_found = True
            st.info("📧 Email taken from seminar file 'E Mail' column")
        else:
            # Fallback: search for @tu-ilmenau.de in all columns
            for col in merged.columns:
                if merged[col].dtype == 'object':
                    tu_emails = merged[col].astype(str).str.contains('@tu-ilmenau.de', na=False)
                    if tu_emails.any():
                        merged["Email_Final"] = merged[col]
                        email_found = True
                        st.success(f"📧 Email found in column: '{col}' (@tu-ilmenau.de emails detected)")
                        break
        
        if not email_found:
            merged["Email_Final"] = "N/A"
            st.error("⚠️ No email column found")
        
        # Clean email column - only keep @tu-ilmenau.de emails
        if email_found:
            merged["Email_Final"] = merged["Email_Final"].apply(
                lambda x: x if (pd.notna(x) and '@tu-ilmenau.de' in str(x)) else "N/A"
            )
            
            # Show statistics
            valid_emails = merged["Email_Final"][merged["Email_Final"] != "N/A"].count()
            total_students = len(merged)
            st.info(f"📊 Found {valid_emails} valid @tu-ilmenau.de emails out of {total_students} students")
        
        # Rename for final table
        merged["E Mail"] = merged["Email_Final"]
        
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
            st.metric("Lowest Grade", f"{final_df['Total Grade'].min():.2f}")
        
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
        
        # Error details
        with st.expander("Error Details"):
            st.exception(e)

else:
    st.info("👆 Please upload both Exam and Seminar CSV files.")
