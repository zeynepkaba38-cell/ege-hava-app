import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# 1. Sayfa Ayarları ve Tema
st.set_page_config(
    page_title="EgeHava - Akıllı Bölgesel Rehber",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .activity-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 5px solid #0083b0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .sea-temp-box {
        background: linear-gradient(135deg, #00b4db, #0083b0);
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Logolu Başlık
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("""
    <svg width="70" height="70" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="35" fill="#ff8c00" />
        <path d="M 15 65 Q 35 50 50 65 T 85 65 L 85 85 L 15 85 Z" fill="#0083b0" opacity="0.8"/>
        <path d="M 15 75 Q 35 60 50 75 T 85 75 L 85 85 L 15 85 Z" fill="#00b4db"/>
    </svg>
    """, unsafe_allow_html=True)

with col_title:
    st.title("EgeHava & Akıllı Aktivite Rehberi")
    st.caption("Mevsime Duyarlı Hava Durumu, Deniz Sıcaklığı ve Yol Tarifi Entegrasyonu")

st.divider()

# Sidebar / Yan Menü
st.sidebar.header("📍 Konum ve Tarih Seçimi")
sehir = st.sidebar.selectbox("Şehir Seçin", ["İzmir", "Muğla", "Aydın"])
tarih = st.sidebar.date_input("Tarih Seçin", datetime.date.today())

# Mevsim Tespiti (Ay Bilgisine Göre)
secilen_ay = tarih.month
is_summer = secilen_ay in [5, 6, 7, 8, 9]  # Mayıs - Eylül arası YAZ

st.sidebar.divider()
st.sidebar.subheader("⚙️ Gösterge Ayarları")
show_temp = st.sidebar.checkbox("Sıcaklık", value=True)
show_wind = st.sidebar.checkbox("Rüzgar Hızı", value=True)
show_humidity = st.sidebar.checkbox("Nem Oranı", value=True)

# Veri Seti (Yaz/Kış Aktiviteleri, Koordinatlar ve Deniz Sıcaklıkları)
mekanlar = [
    # İZMİR - Yaz
    {"sehir": "İzmir", "ad": "Çeşme Ilıca Plajı", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 38.3075, "lon": 26.3572, "deniz_temp": 24},
    {"sehir": "İzmir", "ad": "Alaçatı Rüzgar Sörfü Alanı", "tip": "Yaz", "kat": "Rüzgar Sörfü", "lat": 38.2520, "lon": 26.3880, "deniz_temp": 23},
    {"sehir": "İzmir", "ad": "Foça Eski Foça Koyu", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 38.6703, "lon": 26.7570, "deniz_temp": 22},
    # İZMİR - Kış
    {"sehir": "İzmir", "ad": "Efes Antik Kenti (Selçuk)", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 37.9411, "lon": 27.3419, "deniz_temp": None},
    {"sehir": "İzmir", "ad": "Balçova Termal Tesisleri", "tip": "Kış", "kat": "Termal & Spa", "lat": 38.3892, "lon": 27.0425, "deniz_temp": None},
    {"sehir": "İzmir", "ad": "Kordon Boyu Yürüyüş Yolu", "tip": "Kış", "kat": "Sahil Yürüyüşü", "lat": 38.4322, "lon": 27.1353, "deniz_temp": None},

    # MUĞLA - Yaz
    {"sehir": "Muğla", "ad": "Fethiye Ölüdeniz", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 36.5492, "lon": 29.1156, "deniz_temp": 26},
    {"sehir": "Muğla", "ad": "Akyaka Rüzgar Sörfü Plajı", "tip": "Yaz", "kat": "Rüzgar Sörfü", "lat": 37.0505, "lon": 28.3245, "deniz_temp": 24},
    # MUĞLA - Kış
    {"sehir": "Muğla", "ad": "Sultaniye Kaplıcaları (Köyceğiz)", "tip": "Kış", "kat": "Termal & Spa", "lat": 36.9214, "lon": 28.5833, "deniz_temp": None},
    {"sehir": "Muğla", "ad": "Marmaris Kalesi & Eski Çarşı", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 36.8508, "lon": 28.2725, "deniz_temp": None},

    # AYDIN - Yaz
    {"sehir": "Aydın", "ad": "Kuşadası Kadınlar Denizi", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 37.8483, "lon": 27.2458, "deniz_temp": 25},
    # AYDIN - Kış
    {"sehir": "Aydın", "ad": "Afrodisias Antik Kenti", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 37.6403, "lon": 28.7233, "deniz_temp": None},
]

df_mekanlar = pd.DataFrame(mekanlar)

# Mevsime ve Şehre Göre Filtreleme
mevsim_tur = "Yaz" if is_summer else "Kış"
filtered_df = df_mekanlar[(df_mekanlar["sehir"] == sehir) & (df_mekanlar["tip"] == mevsim_tur)]

# Sıcaklık Simülasyonu
base_temp = 28 if is_summer else 14
sim_temp = base_temp + np.random.randint(-2, 3)

# 1. METRİKLER VE HAVA DURUMU
st.subheader(f"📊 {sehir} İçin {tarih.strftime('%d.%m.%Y')} Hava Durumu")
cols = st.columns(3)
if show_temp:
    cols[0].metric("Hava Sıcaklığı", f"{sim_temp} °C", "Mevsim Normali")
if show_wind:
    cols[1].metric("Rüzgar Hızı", "18 km/s", "Sörfe Uygun" if is_summer else "Orta Rüzgarlı")
if show_humidity:
    cols[2].metric("Nem Oranı", "%55", "Ferah")

st.divider()

# 2. AKTİVİTE ÖNERİLERİ VE HARİTA
col_left, col_right = st.columns([1, 1])

with col_left:
    if is_summer:
        st.subheader("☀️ Yaz Ayı Aktivite & Mekan Önerileri")
        st.info("💡 Tarih seçiminiz yaz dönemine denk geldiği için plajlar, koylar ve su sporları listelenmiştir.")
    else:
        st.subheader("❄️ Kış Ayı Aktivite & Mekan Önerileri")
        st.warning("💡 Tarih seçiminiz kış dönemine denk geldiği için kültür rotaları, termal kaplıcalar ve yürüyüş yolları listelenmiştir.")

    for idx, row in filtered_df.iterrows():
        # Google Maps Yol Tarifi Linki
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={row['lat']},{row['lon']}"
        
        st.markdown(f"""
        <div class="activity-card">
            <h4>📍 {row['ad']}</h4>
            <p><b>Kategori:</b> {row['kat']}</p>
            <a href="{gmaps_url}" target="_blank" style="text-decoration:none;">
                <button style="background-color:#0083b0; color:white; border:none; padding:6px 12px; border-radius:5px; cursor:pointer;">
                    🗺️ Google Maps İle Yol Tarifi Al
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Yaz Mevsimindeysek Deniz Sıcaklığını Göster
        if is_summer and row['deniz_temp'] is not None:
            st.markdown(f"""
            <div class="sea-temp-box">
                🌊 Tahmini Deniz Suyu Sıcaklığı: <b>{row['deniz_temp']} °C</b>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("🗺️ Lokasyon Haritası")
    if not filtered_df.empty:
        fig = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lon",
            hover_name="ad",
            hover_data=["kat"],
            color_discrete_sequence=["#ff7f50" if is_summer else "#0083b0"],
            zoom=8,
            height=450
        )
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0, "t":0, "l":0, "b":0}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Bu kriterlere uygun mekan bulunamadı.")
