import streamlit as st

# Set konfigurasi halaman harus dipanggil paling awal
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

# Impor modul halaman
import analisiseda
import analisislanjut

def main():
    st.sidebar.title("Navigasi Dashboard")
    page = st.sidebar.selectbox("Pilih Halaman", ["Eksplorasi Data", "Analisis Lanjutan"])
    
    if page == "Eksplorasi Data":
        analisiseda.show_eda()
    elif page == "Analisis Lanjutan":
        analisislanjut.show_advanced_analysis()

if __name__ == "__main__":
    main()
