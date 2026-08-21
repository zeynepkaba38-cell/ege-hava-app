import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="EgeHava - Tüm Ege Bölgesi Akıllı Rehberi",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Doğal Yeşil & Mavi Renk Paleti (CSS)
st.markdown("""
<style>
    /* Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
    }
    /* Kart Tasarımları - Orman Yeşili Barlı */
    .activity-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        border-left: 6px solid #059669;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.08);
    }
    /* Deniz Sıcaklığı Kutusu - Deniz Mavisi */
    .sea-temp-box {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 8px;
        margin-top: 8px;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
    }
    /* Yol Tarifi Butonu - Yeşil / Mavi */
    .gmaps-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        border: none;
        padding: 8px 14px;
        border-radius: 6px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin-top: 6px;
        box-shadow: 0 3px 6px rgba(16, 185, 129, 0.3);
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #a7f3d0;
        border-radius: 10px;
        padding: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# Head Banner (Yeşil & Mavi Logo)
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("""
    <svg width="75" height="75" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="35" fill="#10b981" />
        <path d="M 15 65 Q 35 50 50 65 T 85 65 L 85 85 L 15 85 Z" fill="#0284c7" opacity="0.9"/>
        <path d="M 15 75 Q 35 60 50 75 T 85 75 L 85 85 L 15 85 Z" fill="#38bdf8"/>
    </svg>
    """, unsafe_allow_html=True)

with col_title:
    st.title("EgeHava & 8 Şehir Akıllı Aktivite Rehberi")
    st.caption("Doğal Yeşil & Mavi Tema | Sıcaklık Grafiği, Canlı Harita ve Yol Tarifi Entegrasyonu")

st.divider()

# Sidebar / Yan Menü (8 Şehir)
st.sidebar.header("📍 Konum ve Tarih Seçimi")
ege_sehırleri = [
    "İzmir", "Muğla", "Aydın", "Manisa", 
    "Denizli", "Afyonkarahisar", "Uşak", "Kütahya"
]
sehir = st.sidebar.selectbox("Şehir Seçin", ege_sehırleri)
tarih = st.sidebar.date_input("Tarih Seçin", datetime.date.today())

# Mevsim Tespiti
secilen_ay = tarih.month
is_summer = secilen_ay in [5, 6, 7, 8, 9]

st.sidebar.divider()
st.sidebar.subheader("⚙️ Gösterge Ayarları")
show_temp = st.sidebar.checkbox("Sıcaklık", value=True)
show_wind = st.sidebar.checkbox("Rüzgar Hızı", value=True)
show_humidity = st.sidebar.checkbox("Nem Oranı", value=True)

# 8 ŞEHRİ İÇEREN VERİ SETİ
mekanlar = [
    # 1. İZMİR
    {"sehir": "İzmir", "ad": "Çeşme Ilıca Plajı", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 38.3075, "lon": 26.3572, "deniz_temp": 24},
    {"sehir": "İzmir", "ad": "Alaçatı Rüzgar Sörfü Alanı", "tip": "Yaz", "kat": "Rüzgar Sörfü", "lat": 38.2520, "lon": 26.3880, "deniz_temp": 23},
    {"sehir": "İzmir", "ad": "Efes Antik Kenti (Selçuk)", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 37.9411, "lon": 27.3419, "deniz_temp": None},
    {"sehir": "İzmir", "ad": "Balçova Termal Tesisleri", "tip": "Kış", "kat": "Termal & Spa", "lat": 38.3892, "lon": 27.0425, "deniz_temp": None},

    # 2. MUĞLA
    {"sehir": "Muğla", "ad": "Fethiye Ölüdeniz", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 36.5492, "lon": 29.1156, "deniz_temp": 26},
    {"sehir": "Muğla", "ad": "Akyaka Rüzgar Sörfü Plajı", "tip": "Yaz", "kat": "Rüzgar Sörfü", "lat": 37.0505, "lon": 28.3245, "deniz_temp": 24},
    {"sehir": "Muğla", "ad": "Sultaniye Kaplıcaları (Köyceğiz)", "tip": "Kış", "kat": "Termal & Spa", "lat": 36.9214, "lon": 28.5833, "deniz_temp": None},
    {"sehir": "Muğla", "ad": "Marmaris Kalesi", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 36.8508, "lon": 28.2725, "deniz_temp": None},

    # 3. AYDIN
    {"sehir": "Aydın", "ad": "Kuşadası Kadınlar Denizi", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 37.8483, "lon": 27.2458, "deniz_temp": 25},
    {"sehir": "Aydın", "ad": "Didim Altınkum Plajı", "tip": "Yaz", "kat": "Plaj & Deniz", "lat": 37.3575, "lon": 27.2831, "deniz_temp": 24},
    {"sehir": "Aydın", "ad": "Afrodisias Antik Kenti", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 37.6403, "lon": 28.7233, "deniz_temp": None},

    # 4. MANİSA
    {"sehir": "Manisa", "ad": "Spil Dağı Milli Parkı", "tip": "Yaz", "kat": "Doğa Yürüyüşü", "lat": 38.5601, "lon": 27.4485, "deniz_temp": None},
    {"sehir": "Manisa", "ad": "Kula Volkanik Jeoparkı", "tip": "Yaz", "kat": "Doğa Gezisi", "lat": 38.5828, "lon": 28.6142, "deniz_temp": None},
    {"sehir": "Manisa", "ad": "Sardes Antik Kenti", "tip": "Kış", "kat": "Kültür & Tarih", "lat": 38.4883, "lon": 28.0403, "deniz_temp": None},
    {"sehir": "Manisa", "ad": "Kurşunlu Kaplıcaları", "tip": "Kış", "kat": "Termal & Spa", "lat": 38.4528, "lon": 28.1408, "deniz_temp": None},

    # 5. DENİZLİ
    {"sehir": "Denizli", "ad": "Pamukkale Travertenleri", "tip": "Yaz", "kat": "Kültür & Doğa", "lat": 37.9249, "lon": 29.1238, "deniz_temp": None},
    {"sehir": "Denizli", "ad": "Kleopatra Antik Havuzu", "tip": "Yaz", "kat": "Doğal Yüzme", "lat": 37.9268, "lon": 29.1245, "deniz_temp": None},
    {"sehir": "Denizli", "ad": "Karahayıt Termal Tesisleri", "tip": "Kış", "kat": "Termal & Spa", "lat": 37.9622, "lon": 29.1031, "deniz_temp": None},

    # 6. AFYONKARAHİSAR
    {"sehir": "Afyonkarahisar", "ad": "Frig Vadisi Göynük", "tip": "Yaz", "kat": "Doğa Yürüyüşü", "lat": 39.0285, "lon": 30.5283, "deniz_temp": None},
    {"sehir": "Afyonkarahisar", "ad": "Gazlıgöl Termal Kaplıcaları", "tip": "Kış", "kat": "Termal & Spa", "lat": 38.9388, "lon": 30.5050, "deniz_temp": None},

    # 7. UŞAK
    {"sehir": "Uşak", "ad": "Ulubey Kanyonu (Cam Teras)", "tip": "Yaz", "kat": "Doğa Yürüyüşü", "lat": 38.4230, "lon": 29.2940, "deniz_temp": None},
    {"sehir": "Uşak", "ad": "Kayaağıl Termal Tesisleri", "tip": "Kış", "kat": "Termal & Spa", "lat": 38.6410, "lon": 29.3520, "deniz_temp": None},

    # 8. KÜTAHYA
    {"sehir": "Kütahya", "ad": "Aizanoi Antik Kenti", "tip": "Yaz", "kat": "Kültür & Tarih", "lat": 39.2012, "lon": 29.6120, "deniz_temp": None},
    {"sehir": "Kütahya", "ad": "Yoncalı Termal Kaplıcaları", "tip": "Kış", "kat": "Termal & Spa", "lat": 39.4620, "lon": 29.8650, "deniz_temp": None},
]

df_mekanlar = pd.DataFrame(mekanlar)

# İç Ege Hesaplaması
ic_ege = ["Afyonkarahisar", "Kütahya", "Uşak", "Denizli"]
is_inland = sehir in ic_ege

base_temp = (25 if is_inland else 28) if is_summer else (8 if is_inland else 14)
sim_temp = base_temp + np.random.randint(-1, 2)

# 1. METRİKLER VE HAVA DURUMU
st.subheader(f"📊 {sehir} İçin {tarih.strftime('%d.%m.%Y')} Hava Durumu")
cols = st.columns(3)
if show_temp:
    cols[0].metric("Hava Sıcaklığı", f"{sim_temp} °C", "Mevsim Normali")
if show_wind:
    cols[1].metric("Rüzgar Hızı", "14 km/s", "Ferah Rüzgarlı")
if show_humidity:
    cols[2].metric("Nem Oranı", "%45" if is_inland else "%60", "Dengeli")

st.divider()

# 2. 7 GÜNLÜK SICAKLIK TAHMİN GRAFİĞİ (YENİ EKLENDİ)
st.subheader("📈 7 Günlük Sıcaklık Değişim Trendi")
gunler = [tarih + datetime.timedelta(days=i) for i in range(7)]
gun_isimleri = [g.strftime("%d %b") for g in gunler]

# Rastgele Gerçekçi Sıcaklık Değişimi
np.random.seed(len(sehir) + secilen_ay)
sıcaklıklar = [sim_temp + int(np.random.randint(-2, 3)) for _ in range(7)]

fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(
    x=gun_isimleri,
    y=sıcaklıklar,
    mode='lines+markers+text',
    text=[f"{t}°C" for t in sıcaklıklar],
    textposition="top center",
    line=dict(color='#059669', width=3, shape='spline'),
    marker=dict(size=8, color='#0284c7')
))
fig_temp.update_layout(
    xaxis_title="Günler",
    yaxis_title="Sıcaklık (°C)",
    height=250,
    margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_temp, use_container_width=True)

st.divider()

# 3. AKTİVİTE SEÇİM PANELERİ
city_df = df_mekanlar[df_mekanlar["sehir"] == sehir]
mevcut_kategoriler = list(city_df["kat"].unique())

st.subheader("🎯 Aktivite Filtreleme ve Seçim Paneli")
col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
    secilen_kategoriler = st.multiselect(
        "Görüntülemek istediğiniz aktivite türlerini seçin:",
        options=mevcut_kategoriler,
        default=mevcut_kategoriler
    )

with col_sel2:
    st.write("**Mevsim Modu:**")
    if is_summer:
        st.success("☀️ Otomatik Yaz Modu Aktif")
    else:
        st.info("❄️ Otomatik Kış Modu Aktif")

filtered_df = city_df[(city_df["kat"].isin(secilen_kategoriler)) & (city_df["tip"] == ("Yaz" if is_summer else "Kış"))]

st.divider()

# 4. AKTİVİTE LİSTESİ VE KESİNTİSİZ HARİTA
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader(f"📌 Önerilen Aktiviteler ({len(filtered_df)})")

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={row['lat']},{row['lon']}"
            
            st.markdown(f"""
            <div class="activity-card">
                <h3 style="margin:0; color:#064e3b;">📍 {row['ad']}</h3>
                <p style="margin:4px 0; color:#374151;"><b>Aktivite Türü:</b> {row['kat']}</p>
                <a href="{gmaps_url}" target="_blank" class="gmaps-btn">
                    🗺️ Google Maps İle Yol Tarifi Al
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            if is_summer and row['deniz_temp'] is not None:
                st.markdown(f"""
                <div class="sea-temp-box">
                    🌊 Tahmini Deniz Suyu Sıcaklığı: {row['deniz_temp']} °C
                </div>
                """, unsafe_allow_html=True)
            st.write("")
    else:
        st.warning("Seçtiğiniz kriterlere uygun aktivite bulunamadı. Lütfen yukarıdan farklı bir aktivite türü seçin.")

with col_right:
    st.subheader("🗺️ Canlı Harita Görünümü")
    if not filtered_df.empty:
        # Sorunsuz Çalışan Open-Street-Map Stili
        fig_map = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lon",
            hover_name="ad",
            hover_data=["kat"],
            color="kat",
            color_discrete_sequence=["#059669", "#0284c7", "#10b981", "#0284c7"],
            zoom=8,
            height=480
        )
        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0, "t":0, "l":0, "b":0},
            legend=dict(orient="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_map, use_container_width=True)
