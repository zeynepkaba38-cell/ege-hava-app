import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# 1. Sayfa Ayarları ve Tema
st.set_page_config(
    page_title="EgeHava - Ege Bölgesi Hava ve Etkinlikler",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Kartlar, Büyüteçler ve UI Tasarımı
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card-blue { background-color: #e3f2fd; border-top: 4px solid #1e88e5; padding: 12px; border-radius: 8px; }
    .card-red { background-color: #ffebee; border-top: 4px solid #e53935; padding: 12px; border-radius: 8px; }
    .card-yellow { background-color: #fffde7; border-top: 4px solid #fdd835; padding: 12px; border-radius: 8px; }
    .activity-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Ege Bölgesi 8 İl Veri Tabanı (Koordinat ve Örnek Veriler)
EGE_SEHIRLERI = {
    "İzmir": {"lat": 38.4237, "lon": 27.1428, "temp": 31, "durum": "Açık, Güneşli", "nem": "%45", "ruzgar": "20 km/h NW", "renk": "#1e88e5"},
    "Aydın": {"lat": 37.8560, "lon": 27.8416, "temp": 33, "durum": "Açık, Güneşli", "nem": "%40", "ruzgar": "18 km/h N", "renk": "#e53935"},
    "Muğla": {"lat": 37.2153, "lon": 28.3636, "temp": 29, "durum": "Açık, Güneşli", "nem": "%49", "ruzgar": "22 km/h NW", "renk": "#fdd835"},
    "Manisa": {"lat": 38.6191, "lon": 27.4289, "temp": 32, "durum": "Az Bulutlu", "nem": "%42", "ruzgar": "15 km/h NE", "renk": "#43a047"},
    "Denizli": {"lat": 37.7765, "lon": 29.0864, "temp": 30, "durum": "Güneşli", "nem": "%38", "ruzgar": "12 km/h E", "renk": "#fb8c00"},
    "Kütahya": {"lat": 39.4167, "lon": 29.9833, "temp": 26, "durum": "Parçalı Bulutlu", "nem": "%55", "ruzgar": "14 km/h W", "renk": "#8e24aa"},
    "Uşak": {"lat": 38.6823, "lon": 29.4082, "temp": 27, "durum": "Açık", "nem": "%50", "ruzgar": "16 km/h NW", "renk": "#00acc1"},
    "Afyonkarahisar": {"lat": 38.7507, "lon": 30.5567, "temp": 25, "durum": "Parçalı Bulutlu", "nem": "%58", "ruzgar": "19 km/h NE", "renk": "#3949ab"}
}

# 3. SOL YAN MENÜ (3 Çizgili Hamburger Menüye Dokunulduğunda Açılan Panel)
st.sidebar.image("https://img.icons8.com/color/96/sun--v1.png", width=60)
st.sidebar.title("☀️ EgeHava Ayarları")
st.sidebar.markdown("---")

st.sidebar.subheader("📍 Bölge ve Şehir Seçimi")
secilen_sehirler = st.sidebar.multiselect(
    "Görüntülenecek Şehirleri Seçin (Max 8 İl):",
    options=list(EGE_SEHIRLERI.keys()),
    default=["İzmir", "Aydın", "Muğla"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Görünüm Ayarları")
harita_tipi = st.sidebar.selectbox("Harita Stili:", ["Carto-Positron", "Open-Street-Map", "Satellite"])
birim_secimi = st.sidebar.radio("Sıcaklık Birimi:", ["Santigrat (°C)", "Fahrenheit (°F)"])
karanlik_mod = st.sidebar.checkbox("Karanlık Mod Arayüzü")

# 4. ÜST BAŞLIK BARI
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("🌤️ EgeHava — Ege Bölgesi Hava ve Etkinlikler")
with header_col2:
    st.date_input("Tarih Seçimi", value=pd.to_datetime("2026-08-15"))

st.markdown("---")

# 5. ANA PANOLAR (3 SÜTUNLU LAYOUT)
col_left, col_mid, col_right = st.columns([1.3, 1.2, 1.1])

# ----------------------------------------------------
# SOL SÜTUN: Şehir Kartları ve Haftalık Sıcaklık Grafiği
# ----------------------------------------------------
with col_left:
    st.subheader("Bölgesel Hava Durumu")
    
    # Seçilen Şehirlerin Kartlarını Dinamik Basma
    if secilen_sehirler:
        card_cols = st.columns(len(secilen_sehirler))
        for idx, sehir in enumerate(secilen_sehirler):
            data = EGE_SEHIRLERI[sehir]
            with card_cols[idx]:
                st.markdown(f"**{sehir.upper()}**")
                st.markdown(f"## {data['temp']}°C")
                st.caption(f"☀️ {data['durum']}")
                st.text(f"💧 {data['nem']}")
                st.text(f"💨 {data['ruzgar']}")
    else:
        st.warning("Lütfen sol menüden en az bir şehir seçin.")

    st.markdown("---")
    st.subheader("Haftalık Sıcaklık Grafiği")
    
    # Dinamik Plotly Çizgi Grafiği
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    fig_line = go.Figure()

    for sehir in secilen_sehirler:
        base_temp = EGE_SEHIRLERI[sehir]["temp"]
        temp_variation = base_temp + np.random.randint(-3, 4, size=7)
        fig_line.add_trace(go.Scatter(
            x=gunler, y=temp_variation,
            mode='lines+markers',
            name=sehir,
            line=dict(width=3)
        ))

    fig_line.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ----------------------------------------------------
# ORTA SÜTUN: İnteraktif Ege Bölgesi Haritası
# ----------------------------------------------------
with col_mid:
    st.subheader("Ege Bölgesi Harita Görünümü")
    
    # Harita için Veri Hazırlığı
    map_data = []
    for sehir, info in EGE_SEHIRLERI.items():
        if sehir in secilen_sehirler:
            map_data.append({
                "Şehir": sehir,
                "lat": info["lat"],
                "lon": info["lon"],
                "Sıcaklık": f"{info['temp']}°C",
                "Durum": info["durum"]
            })
    
    df_map = pd.DataFrame(map_data)
    
    if not df_map.empty:
        fig_map = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            hover_name="Şehir",
            hover_data=["Sıcaklık", "Durum"],
            size_max=15,
            zoom=6.8,
            center={"lat": 38.0, "lon": 28.0},
            mapbox_style="carto-positron"
        )
        fig_map.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------------------------
# SAĞ SÜTUN: Bugünkü Etkinlik Önerileri
# ----------------------------------------------------
with col_right:
    st.subheader("Bugünkü Etkinlik Önerileri")
    st.caption("(Ege Bölgesi Genel)")
    
    act_col1, act_col2 = st.columns(2)
    
    with act_col1:
        st.markdown("""
        <div class="activity-card">
            <h4>⛵ YELKENLİ</h4>
            <p><small>Seferihisar'da yelken keyfi</small></p>
        </div>
        <div class="activity-card">
            <h4>🏄‍♂️ RÜZGAR SÖRFLÜ</h4>
            <p><small>Rüzgarda sörf</small></p>
        </div>
        <div class="activity-card">
            <h4>🏖️ PLAJ KEYFİ</h4>
            <p><small>Çeşme ve Bodrum plajları</small></p>
        </div>
        """, unsafe_allow_html=True)
        
    with act_col2:
        st.markdown("""
        <div class="activity-card">
            <h4>🥾 DOĞA YÜRÜYÜŞÜ</h4>
            <p><small>Muğla/Bafa rotası</small></p>
        </div>
        <div class="activity-card">
            <h4>🏛️ TARİHİ GEZİ</h4>
            <p><small>Efes & Hierapolis</small></p>
        </div>
        <div class="activity-card">
            <h4>🚴 BİSİKLET</h4>
            <p><small>Sahil şeridi turu</small></p>
        </div>
        """, unsafe_allow_html=True)

# 6. ALT ŞERİT: 7 GÜNLÜK HAVA ÖZETİ VE GERİ BİLDİRİM
st.markdown("---")
bot_col1, bot_col2 = st.columns([4, 1])

with bot_col1:
    st.markdown("**EGE BÖLGESİ 7 GÜNLÜK GENEL HAVA TAHMİNİ**")
    forecast_cols = st.columns(7)
    for i, col in enumerate(forecast_cols):
        with col:
            st.caption(f"{gunler[i]}")
            st.markdown("☀️ 30°C")

with bot_col2:
    if st.button("📩 Öneriler ve Geri Bildirim"):
        st.info("Geri bildirim formuna yönlendiriliyorsunuz...")
