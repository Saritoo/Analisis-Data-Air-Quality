import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def show_advanced_analysis():
    st.title("Analisis Lanjutan")
    st.markdown("""
    Dashboard ini menyajikan cerita dari data kualitas udara dengan fokus pada:
    
    1. **RFM-Like Analysis untuk PM2.5:**  
       - **Recency:** Jarak hari dari data terbaru yang melebihi ambang batas.  
       - **Frequency:** Berapa kali PM2.5 melebihi ambang batas dalam 30 hari terakhir.  
       - **Magnitude:** Rata-rata selisih PM2.5 di atas ambang batas.
    2. **Klasifikasi Kategori Harian:**  
       Pengelompokan harian PM2.5 ke dalam kategori (Baik, Sedang, Tidak Sehat, Sangat Tidak Sehat, Berbahaya) berdasarkan ambang WHO.
    3. **Rekap Tahunan:**  
       Ilustrasi tren perubahan kualitas udara dari tahun ke tahun, dilengkapi dengan kesimpulan otomatis berdasarkan nilai rata-rata PM2.5.
    """)

    # Muat data (pastikan file berada di folder Dashboard)
    df = pd.read_csv("Dashboard/data_AirQuality_clean.csv", parse_dates=["datetime"])
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Sidebar: Filter Data
    st.sidebar.header("Filter Data")
    # Filter berdasarkan stasiun
    station_options = sorted(df['station'].unique().tolist())
    selected_station = st.sidebar.selectbox("Pilih Stasiun", station_options, index=0)
    
    # Filter data berdasarkan stasiun yang dipilih
    df_station = df[df['station'] == selected_station].copy()
    
    # Filter berdasarkan rentang tanggal
    min_date = df_station['datetime'].min().date()
    max_date = df_station['datetime'].max().date()
    date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        df_station = df_station[(df_station['datetime'].dt.date >= start_date) & 
                            (df_station['datetime'].dt.date <= end_date)]
    else:
        start_date = min_date
        end_date = max_date

    st.markdown(f"### Menampilkan data untuk stasiun **{selected_station}** dari **{start_date}** sampai **{end_date}**")
    
    # Buat kolom 'date' untuk perhitungan harian
    df_station['date'] = pd.to_datetime(df_station['datetime'].dt.date)
    
    # Hitung rata-rata harian untuk polutan (fokus pada PM2.5, namun juga menghitung yang lain untuk rekap)
    daily_avg = df_station.groupby('date').agg({
        'PM2.5': 'mean',
        'PM10': 'mean',
        'SO2': 'mean',
        'NO2': 'mean',
        'CO': 'mean',
        'O3': 'mean'
    }).reset_index()
    daily_avg['year'] = daily_avg['date'].dt.year

    #############################
    # 1. RFM-Like Analysis untuk PM2.5
    #############################
    st.subheader("RFM-Like Analysis untuk PM2.5")
    threshold_pm25 = 15  # Ambang batas WHO untuk PM2.5 (µg/m³)
    
    # Recency: Hitung selisih hari antara setiap tanggal dengan tanggal terakhir
    daily_avg['recency'] = (daily_avg['date'].max() - daily_avg['date']).dt.days
    
    # Frequency & Magnitude: Hitung dalam 30 hari terakhir
    end_date_data = daily_avg['date'].max()
    start_date_30 = end_date_data - pd.Timedelta(days=30)
    last_30days = daily_avg[daily_avg['date'] >= start_date_30]
    frequency = last_30days['PM2.5'].gt(threshold_pm25).sum()
    exceed_values = last_30days[last_30days['PM2.5'] > threshold_pm25]['PM2.5']
    magnitude = (exceed_values - threshold_pm25).mean() if not exceed_values.empty else 0

    st.markdown(f"""
    **RFM-Like Analysis (PM2.5):**  
    - **Recency:** Data terbaru yang melebihi ambang batas terjadi {daily_avg['recency'].min()} hari yang lalu.  
    - **Frequency:** Dalam 30 hari terakhir, terdapat **{frequency}** hari dimana PM2.5 melebihi ambang batas {threshold_pm25} µg/m³.  
    - **Magnitude:** Rata-rata selisih PM2.5 di atas ambang batas adalah **{magnitude:.2f} µg/m³**.
    """)
    
    #############################
    # 2. Klasifikasi Kategori PM2.5 Harian
    #############################
    st.subheader("Klasifikasi Kategori PM2.5 Harian")
    bins = [0, 15, 35, 55, 150, np.inf]
    labels = ['Baik', 'Sedang', 'Tidak Sehat', 'Sangat Tidak Sehat', 'Berbahaya']
    daily_avg['PM2.5_category'] = pd.cut(daily_avg['PM2.5'], bins=bins, labels=labels)
    
    # Visualisasi distribusi kategori PM2.5 menggunakan Plotly
    cat_counts = daily_avg['PM2.5_category'].value_counts().reindex(labels).reset_index()
    cat_counts.columns = ['Kategori', 'Jumlah Hari']
    fig_cat = px.bar(cat_counts, x='Kategori', y='Jumlah Hari',
                     color='Jumlah Hari', color_continuous_scale='viridis',
                     title=f"Distribusi Kategori PM2.5 Harian - {selected_station}")
    st.plotly_chart(fig_cat, use_container_width=True)
    
    #############################
    # 3. Rekap Tahunan Berdasarkan Standar WHO
    #############################
    st.subheader("Rekap Tahunan Berdasarkan Standar WHO")
    thresholds = {
        'PM2.5': 15,   # µg/m³
        'PM10': 45,    # µg/m³
        'SO2': 20,     # µg/m³
        'NO2': 25,     # µg/m³
        'CO': 4,       # mg/m³
        'O3': 100      # µg/m³
    }
    
    summary = daily_avg.groupby('year').agg(
        total_days = ('date', 'count'),
        avg_PM25 = ('PM2.5', 'mean'),
        avg_PM10 = ('PM10', 'mean'),
        avg_SO2  = ('SO2', 'mean'),
        avg_NO2  = ('NO2', 'mean'),
        avg_CO   = ('CO', 'mean'),
        avg_O3   = ('O3', 'mean')
    ).reset_index()
    
    # Hitung jumlah hari exceed untuk PM2.5 dan persentasenya
    summary["exceed_PM2.5"] = daily_avg.groupby('year')['PM2.5'].apply(lambda x: (x > thresholds['PM2.5']).sum()).values
    summary["pct_exceed_PM2.5"] = summary["exceed_PM2.5"] / summary["total_days"] * 100
    
    # Visualisasi rata-rata harian PM2.5 per tahun dengan garis ambang
    fig_avg = px.bar(summary, x='year', y='avg_PM25', color='avg_PM25',
                     color_continuous_scale='Blues',
                     title=f"Rata-rata Harian PM2.5 per Tahun - {selected_station}")
    fig_avg.add_hline(y=thresholds['PM2.5'], line_dash="dash", line_color="red",
                      annotation_text=f"Threshold PM2.5 ({thresholds['PM2.5']} µg/m³)")
    st.plotly_chart(fig_avg, use_container_width=True)
    
    # Visualisasi persentase hari exceed untuk PM2.5 per tahun
    fig_pct = px.line(summary, x='year', y='pct_exceed_PM2.5', markers=True,
                      title=f"Persentase Hari Melebihi Ambang Batas PM2.5 per Tahun - {selected_station}",
                      color_discrete_sequence=["green"])
    fig_pct.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_pct, use_container_width=True)
    
    #############################
    # Kesimpulan Otomatis Kualitas Udara
    #############################
    st.markdown("### Kesimpulan Kualitas Udara")
    # Hitung rata-rata PM2.5 dari seluruh periode data yang difilter
    overall_avg_pm25 = daily_avg['PM2.5'].mean()
    
    # Tentukan klasifikasi berdasarkan nilai rata-rata PM2.5 (sesuai ambang WHO)
    if overall_avg_pm25 < 15:
        quality = "Baik"
        message = "Kualitas udara tergolong **baik**. Nilai PM2.5 berada di bawah ambang batas WHO."
    elif overall_avg_pm25 < 35:
        quality = "Sedang"
        message = "Kualitas udara **sedang**. Meskipun masih dalam batas, ada peningkatan yang perlu diperhatikan."
    elif overall_avg_pm25 < 55:
        quality = "Tidak Sehat"
        message = "Kualitas udara **tidak sehat**. Waspadai potensi dampak kesehatan terutama bagi kelompok rentan."
    elif overall_avg_pm25 < 150:
        quality = "Sangat Tidak Sehat"
        message = "Kualitas udara **sangat tidak sehat**. Aktivitas luar ruangan sebaiknya dikurangi."
    else:
        quality = "Berbahaya"
        message = "Kualitas udara **berbahaya**. Hindari aktivitas di luar ruangan dan ikuti peringatan kesehatan."
    
    st.markdown(f"""
    **Rata-rata PM2.5:** {overall_avg_pm25:.2f} µg/m³  
    **Penilaian Kualitas Udara:** **{quality}**  
    
    {message}
    """)
