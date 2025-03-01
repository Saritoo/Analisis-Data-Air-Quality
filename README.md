# Dicoding Collection Dashboard ✨

Dashboard ini menyajikan analisis interaktif kualitas udara yang telah dipersiapkan menggunakan Streamlit. Dashboard ini menampilkan berbagai insight dari data kualitas udara seperti tren tahunan, pola aktivitas harian & mingguan, pengaruh parameter meteorologi, serta analisis dampak hujan terhadap polusi.

## Setup Environment - Anaconda
Buka terminal/Anaconda Prompt dan jalankan perintah berikut:
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
Jika Anda menggunakan terminal biasa, jalankan perintah berikut:
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
Untuk menjalankan dashboard, pastikan Anda berada di direktori root proyek, kemudian jalankan:
```bash
streamlit run Dashboard/dashboard.py
```

## Struktur Proyek
```
submission_analisdata_SahrulR/
├── Dashboard
│   ├── dashboard.py
│   ├── analisiseda.py
│   ├── analisislanjut.py
│   └── data_AirQuality_clean.csv
├── data
│   ├── hourly_avg_eda.csv
│   ├── weekday_avg_eda.csv
│   └── yearly_avg_eda.csv
├── README.md
├── requirements.txt
└── url.txt
```

## Data Source URL
Lihat file `url.txt` untuk informasi sumber data yang digunakan.

Happy analyzing!
