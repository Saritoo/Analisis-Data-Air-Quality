import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def show_eda():
    st.title("Eksplorasi Data Kualitas Udara")
    st.markdown("""
    **Overview:**
    
    Dashboard ini menyajikan analisis mendalam dari data kualitas udara dengan fitur interaktif. 
    Anda dapat memfilter data berdasarkan rentang tanggal, stasiun, dan memilih parameter polutan atau meteorologi tertentu. 
    Analisis mencakup:
    
    1. **Tren Tahunan & Perbedaan Antar Stasiun:** Melihat perubahan polutan (PM2.5, PM10, NO2) per tahun di setiap stasiun.
    2. **Pola Aktivitas Harian & Mingguan:** Menampilkan fluktuasi polusi sepanjang hari dan antar hari.
    3. **Pengaruh Parameter Meteorologi:** Mengeksplorasi hubungan antara suhu, tekanan, titik embun, dan curah hujan dengan PM2.5.
    4. **Dampak Kondisi Cuaca (Hujan):** Membandingkan rata-rata PM2.5 antara hari hujan dan tanpa hujan.
    """)
    
    # Memuat data bersih (pastikan file ini berada di folder Dashboard)
    df_clean = pd.read_csv("Dashboard/data_AirQuality_clean.csv", parse_dates=["datetime"])
    df_clean['datetime'] = pd.to_datetime(df_clean['datetime'])
    df_clean['weekday'] = df_clean['datetime'].dt.day_name()
    # Sidebar: Filter Data
    st.sidebar.header("Filter Data")
    
    # Filter berdasarkan Rentang Tanggal
    min_date = df_clean["datetime"].min().date()
    max_date = df_clean["datetime"].max().date()
    date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])
    if isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        df_clean = df_clean[(df_clean["datetime"].dt.date >= start_date) & 
                            (df_clean["datetime"].dt.date <= end_date)]
    
    # Filter berdasarkan Stasiun
    station_options = df_clean["station"].unique().tolist()
    selected_stations = st.sidebar.multiselect("Pilih Stasiun", station_options, default=station_options)
    df_clean = df_clean[df_clean["station"].isin(selected_stations)]
    
    ######################################################################
    # 1. Trend Tahunan dan Perbedaan Antar Stasiun
    ######################################################################
    st.subheader("1. Tren Tahunan dan Perbedaan Antar Stasiun")
    st.markdown("Grafik di bawah ini menunjukkan tren rata-rata tahunan untuk polutan yang dipilih di setiap stasiun.")
    
    # Pilih polutan untuk analisis tren
    pollutants = ['PM2.5', 'PM10', 'NO2']
    selected_pollutants = st.sidebar.multiselect("Pilih Polutan untuk Trend Tahunan", pollutants, default=pollutants)
    
    # Hitung rata-rata per tahun per stasiun
    yearly_avg = df_clean.groupby(['year', 'station'])[selected_pollutants].mean().reset_index()
    for pollutant in selected_pollutants:
        fig = px.line(yearly_avg, x='year', y=pollutant, color='station', markers=True,
                      title=f"Tren Rata-rata {pollutant} per Tahun")
        fig.update_layout(xaxis_title="Tahun", yaxis_title=f"Rata-rata {pollutant}")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    ######################################################################
    # 2. Pola Aktivitas Harian dan Mingguan
    ######################################################################
    st.subheader("2. Pola Aktivitas Harian dan Mingguan")
    st.markdown("Pilih polutan untuk melihat pola aktivitas harian dan mingguan. Secara default, menggunakan **PM2.5**.")
    
    selected_pollutant_daily = st.sidebar.selectbox("Pilih Polutan untuk Pola Harian/Mingguan", 
                                                    options=['PM2.5', 'PM10', 'NO2'], index=0)
    
    # Rata-rata polutan per jam
    hourly_avg = df_clean.groupby('hour')[selected_pollutant_daily].mean().reset_index()
    fig_hour = px.line(hourly_avg, x='hour', y=selected_pollutant_daily, markers=True,
                       title=f"Rata-rata {selected_pollutant_daily} per Jam")
    fig_hour.update_layout(xaxis_title="Jam", yaxis_title=f"{selected_pollutant_daily} (µg/m³)",
                             xaxis=dict(tickmode='linear'))
    st.plotly_chart(fig_hour, use_container_width=True)
    
    # Rata-rata polutan per hari dalam minggu
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_avg = df_clean.groupby('weekday')[selected_pollutant_daily].mean().reindex(weekday_order).reset_index()
    fig_weekday = px.bar(weekday_avg, x='weekday', y=selected_pollutant_daily,
                         title=f"Rata-rata {selected_pollutant_daily} per Hari dalam Minggu",
                         color=selected_pollutant_daily, color_continuous_scale='viridis')
    fig_weekday.update_layout(xaxis_title="Hari", yaxis_title=f"{selected_pollutant_daily} (µg/m³)")
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    st.markdown("---")
    
    ######################################################################
    # 3. Pengaruh Parameter Meteorologi terhadap Polusi
    ######################################################################
    st.subheader("3. Pengaruh Parameter Meteorologi terhadap Polusi")
    st.markdown("Eksplorasi hubungan antara parameter meteorologi dan konsentrasi **PM2.5**. Pilih parameter meteorologi yang ingin ditampilkan.")
    
    meteorology = ['TEMP', 'PRES', 'DEWP', 'RAIN']
    selected_met = st.sidebar.multiselect("Pilih Parameter Meteorologi", options=meteorology, default=meteorology)
    
    if len(selected_met) > 0:
        fig, axs = plt.subplots(1, len(selected_met), figsize=(6*len(selected_met), 5))
        if len(selected_met) == 1:
            axs = [axs]
        for i, met in enumerate(selected_met):
            sns.scatterplot(data=df_clean, x=met, y='PM2.5', alpha=0.3, ax=axs[i])
            axs[i].set_title(f"{met} vs PM2.5")
            axs[i].set_xlabel(met)
            axs[i].set_ylabel("PM2.5 (µg/m³)")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Silakan pilih minimal satu parameter meteorologi untuk ditampilkan.")
    
    # Matriks Korelasi antara parameter meteorologi dan polutan
    st.markdown("**Matriks Korelasi:** Hubungan antara parameter meteorologi dan polutan.")
    cols_for_corr = meteorology + pollutants
    corr_matrix = df_clean[cols_for_corr].corr()

    fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale='RdBu',  # ganti 'coolwarm' dengan 'RdBu'
    title="Matriks Korelasi: Meteorologi & Polutan")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")
    
    ######################################################################
    # 4. Dampak Kondisi Cuaca (Hujan) pada Polusi
    ######################################################################
    st.subheader("4. Dampak Kondisi Cuaca (Hujan) pada Polusi")
    st.markdown("Bandingkan rata-rata **PM2.5** antara hari dengan hujan dan tanpa hujan.")
    
    # Opsi filter tambahan untuk kondisi hujan
    show_rain_filter = st.sidebar.checkbox("Filter data berdasarkan kondisi hujan", value=False)
    if show_rain_filter:
        # Pilih status hujan: True (hari hujan) atau False (hari tidak hujan)
        rain_status = st.sidebar.selectbox("Pilih kondisi hujan", options=[True, False], index=0)
        df_filtered = df_clean[df_clean['RAIN'] > 0] if rain_status else df_clean[df_clean['RAIN'] == 0]
        rain_label = "Hari Hujan" if rain_status else "Hari Tanpa Hujan"
    else:
        df_filtered = df_clean.copy()
        rain_label = "Semua Hari"
    
    # Pastikan kolom 'rain_flag' ada
    df_filtered['rain_flag'] = df_filtered['RAIN'] > 0
    rain_pm25 = df_filtered.groupby('rain_flag')['PM2.5'].mean().reset_index()
    fig_rain = px.bar(
        rain_pm25, 
        x='rain_flag', 
        y='PM2.5',
        title=f"Rata-rata PM2.5: {rain_label}",
        labels={
        "rain_flag": "Hujan (True = Ada, False = Tidak Ada)",
        "PM2.5": "PM2.5 (µg/m³)"
        },
    color='PM2.5', 
    color_continuous_scale='viridis' 
    )
    st.plotly_chart(fig_rain, use_container_width=True)

    st.subheader("Kesimpulan Insight Interaktif")

    # Widget untuk memilih kategori insight yang ingin ditampilkan
    insight_options = st.multiselect(
        "Pilih kategori insight untuk ditampilkan:",
        options=["Tren Tahunan", "Pola Harian & Mingguan", "Pengaruh Meteorologi", "Dampak Hujan"],
        default=["Tren Tahunan", "Pola Harian & Mingguan", "Pengaruh Meteorologi", "Dampak Hujan"]
    )
    # Tampilkan insight dalam expander sesuai pilihan user
    if "Tren Tahunan" in insight_options:
        with st.expander("Insight: Tren Tahunan"):
            st.write("""
            - Terdapat variasi tren antar stasiun untuk polutan yang dipilih.
            - Tren yang muncul dapat mengindikasikan perbedaan karakteristik antar wilayah.
            """)

    if "Pola Harian & Mingguan" in insight_options:
        with st.expander("Insight: Pola Harian & Mingguan"):
            st.write("""
            - Polutan menunjukkan fluktuasi berdasarkan jam dan hari.
            - Pola ini mengindikasikan pengaruh aktivitas manusia dan kondisi atmosfer.
            """)

    if "Pengaruh Meteorologi" in insight_options:
        with st.expander("Insight: Pengaruh Meteorologi"):
            st.write("""
            - Parameter cuaca seperti suhu, tekanan, titik embun, dan curah hujan memiliki hubungan yang bervariasi dengan konsentrasi PM2.5.
            - Hubungan ini membantu mengidentifikasi kondisi meteorologi yang berpotensi mempengaruhi polusi.
            """)

    if "Dampak Hujan" in insight_options:
        with st.expander("Insight: Dampak Hujan"):
            st.write("""
            - Hujan cenderung menurunkan konsentrasi PM2.5 melalui proses wet deposition.
            - Analisis ini menekankan peran kondisi cuaca dalam mengurangi polusi.
            """)
