import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# 1. Sayfa Ayarları ve Tema
st.set_page_config(
    page_title="EgeHava - Ege Bölgesi Hava ve Akıllı Aktivite Rehberi",
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
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .activity-card:hover {
        border-color: #1e88e5;
        background-color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

# 2. ŞEHİR BAZLI AKTİVİTE MEKANLARI VE KOORDİNAT VERİ TABANI (Google Maps İpuçları)
CITY_ACTIVITIES = {
    "İzmir": {
        "Plaj": [
            {"isim": "Ilıca Plajı (Çeşme)", "lat": 38.3075, "lon": 26.3683, "detay": "Sıcak termal suları ve ince kumuyla ünlü."},
            {"isim": "Akkum Plajı (Seferihisar)", "lat": 38.1961, "lon": 26.8378, "detay": "Rüzgarı ve berrak deniziyle sakin bir koy."}
        ],
        "Sörf": [
            {"isim": "Alaçatı Sörf Merkezi", "lat": 38.2520, "lon": 26.3768, "detay": "Dünyaca ünlü rüzgar sörfü ve kiteboard noktası."}
        ],
        "Yelkenli": [
            {"isim": "Urla Marina / Yılancı Burnu", "lat": 38.3601, "lon": 26.7725, "detay": "Yelken eğitimleri ve yat turları için ideal."}
        ],
        "Yürüyüş": [
            {"isim": "Balçova Terapi Ormanı", "lat": 38.3750, "lon": 27.0420, "detay": "Doğa içinde şelaleli yürüyüş parkuru."}
        ],
        "Tarih": [
            {"isim": "Efes Antik Kenti (Selçuk)", "lat": 37.9485, "lon": 27.3680, "detay": "Dünya mirası UNESCO antik kenti."}
        ],
        "Bisiklet": [
            {"isim": "Kordon Boyu / Bostanlı Sahil", "lat": 38.4350, "lon": 27.1380, "detay": "Kesintisiz sahil bisiklet yolu."}
        ]
    },
    "Muğla": {
        "Plaj": [
            {"isim": "Ölüdeniz Belcekız", "lat": 36.5492, "lon": 29.1165, "detay": "Turkuaz denizi ve lagünüyle ünlü."},
            {"isim": "Iztuzu Plajı (Dalyan)", "lat": 36.7905, "lon": 28.6180, "detay": "Caretta caretta kaplumbağaları koruma alanı."}
        ],
        "Sörf": [
            {"isim": "Akyaka Kitesurf Plajı", "lat": 37.0520, "lon": 28.3220, "detay": "Akyaka'nın sabit rüzgarında uçurtma sörfü."}
        ],
        "Yelkenli": [
            {"isim": "Göcek Marinaları", "lat": 36.7560, "lon": 28.9380, "detay": "Ege'nin en muazzam koylarına açılan yelken kapısı."}
        ],
        "Yürüyüş": [
            {"isim": "Likya Yolu Başlangıcı (Fethiye)", "lat": 36.5750, "lon": 29.1430, "detay": "Tarihi yürüyüş rotasının büyüleyici başlangıcı."}
        ],
        "Tarih": [
            {"isim": "Bodrum Kalesi & Sualtı Müzesi", "lat": 37.0315, "lon": 27.4295, "detay": "Şövalyeler dönemi tarihi kale."}
        ],
        "Bisiklet": [
            {"isim": "Marmaris Yalancıboğaz Rotaları", "lat": 36.8180, "lon": 28.2950, "detay": "Çam ormanları arasında dağ bisikleti."}
        ]
    },
    "Aydın": {
        "Plaj": [
            {"isim": "Altınkum Plajı (Didim)", "lat": 37.3565, "lon": 27.2830, "detay": "Sığ ve altın sarısı kumlu ünlü sahil."},
            {"isim": "Kadınlar Denizi (Kuşadası)", "lat": 37.8420, "lon": 27.2480, "detay": "Kuşadası'nın büyüleyici şehir içi plajı."}
        ],
        "Yürüyüş": [
            {"isim": "Dilek Yarımadası Milli Parkı", "lat": 37.6710, "lon": 27.1650, "detay": "Yeşil ile mavinin birleştiği kanyon rotaları."}
        ],
        "Tarih": [
            {"isim": "Didim Apollon Tapınağı", "lat": 37.3850, "lon": 27.2560, "detay": "Antik çağın en büyük kehanet merkezlerinden."}
        ],
        "Sörf": [{"isim": "Kuşadası Sevgi Plajı", "lat": 37.7850, "lon": 27.2600, "detay": "Rüzgar ve su sporları."}],
        "Yelkenli": [{"isim": "Kuşadası Setur Marina", "lat": 37.8680, "lon": 27.2610, "detay": "Yat ve yelkenli iskelesi."}],
        "Bisiklet": [{"isim": "Bafa Gölü Kıyı Yolu", "lat": 37.5020, "lon": 27.4200, "detay": "Tarihi kaya resimleri arasında sürüş."}]
    }
}

# Varsayılan diğer Ege illeri için genel mekanlar
DEFAULT_SPOTS = {
    "Plaj": [{"isim": "Bölge Sahili", "lat": 38.0, "lon": 27.5, "detay": "En yakın sahil alanı."}],
    "Yürüyüş": [{"isim": "Tabiat Parkı Rotaları", "lat": 38.5, "lon": 28.0, "detay": "Orman içi doğa yürüyüşü."}],
    "Tarih": [{"isim": "Kent Müzesi ve Ören Yeri", "lat": 38.8, "lon": 29.0, "detay": "Bölgenin tarihi mekanları."}],
    "Sörf": [{"isim": "Rüzgar Alan Sahil Şeridi", "lat": 38.2, "lon": 26.8, "detay": "Rüzgar sporları noktası."}],
    "Yelkenli": [{"isim": "Yat Limanı", "lat": 37.9, "lon": 27.2, "detay": "Yelkenli iskelesi."}],
    "Bisiklet": [{"isim": "Şehir İçi Bisiklet Parkuru", "lat": 38.6, "lon": 27.4, "detay": "Güvenli sürüş kulvarı."}]
}

# Ege Bölgesi Temel Verileri
EGE_SEHIRLERI = {
    "İzmir": {"lat": 38.4237, "lon": 27.1428, "base_temp": 31, "durum": "Güneşli", "nem": "%45", "ruzgar": "20 km/h NW"},
    "Aydın": {"lat": 37.8560, "lon": 27.8416, "base_temp": 33, "durum": "Açık", "nem": "%40", "ruzgar": "18 km/h N"},
    "Muğla": {"lat": 37.2153, "lon": 28.3636, "base_temp": 29, "durum": "Güneşli", "nem": "%49", "ruzgar": "22 km/h NW"},
    "Manisa": {"lat": 38.6191, "lon": 27.4289, "base_temp": 32, "durum": "Az Bulutlu", "nem": "%42", "ruzgar": "15 km/h NE"},
    "Denizli": {"lat": 37.7765, "lon": 29.0864, "base_temp": 30, "durum": "Sıcak", "nem": "%38", "ruzgar": "12 km/h E"},
    "Kütahya": {"lat": 39.4167, "lon": 29.9833, "base_temp": 26, "durum": "Parçalı Bulutlu", "nem": "%55", "ruzgar": "14 km/h W"},
    "Uşak": {"lat": 38.6823, "lon": 29.4082, "base_temp": 27, "durum": "Açık", "nem": "%50", "ruzgar": "16 km/h NW"},
    "Afyonkarahisar": {"lat": 38.7507, "lon": 30.5567, "base_temp": 25, "durum": "Parçalı Bulutlu", "nem": "%58", "ruzgar": "19 km/h NE"}
}

# 3. SOL YAN MENÜ
st.sidebar.image("https://img.icons8.com/color/96/sun--v1.png", width=60)
st.sidebar.title("☀️ EgeHava Ayarları")
st.sidebar.markdown("---")

secilen_sehirler = st.sidebar.multiselect(
    "Görüntülenecek Şehirleri Seçin:",
    options=list(EGE_SEHIRLERI.keys()),
    default=["İzmir", "Aydın", "Muğla"]
)

st.sidebar.markdown("---")
harita_tipi = st.sidebar.selectbox("Harita Stili:", ["Carto-Positron", "Open-Street-Map", "Satellite"])

# 4. ÜST BAŞLIK & DİNAMİK TARİH SEÇİMİ
header_col1, header_col2 = st.columns([3, 1.2])
with header_col1:
    st.title("🌤️ EgeHava — Akıllı Hava ve Aktivite Rehberi")
with header_col2:
    secilen_tarih = st.date_input("📅 Tarih Seçimi", value=datetime.date.today())

# Tarihe bağlı dinamik hava değişimi hesabı (Günün koduna göre sıcaklık dalgalanması)
tarih_tohumu = secilen_tarih.day + secilen_tarih.month * 30

st.markdown("---")

# 5. ANA PANEL
col_left, col_mid, col_right = st.columns([1.3, 1.3, 1.1])

# State Hazırlığı (Seçilen Aktivite)
if 'active_activity' not in st.session_state:
    st.session_state['active_activity'] = "Plaj"

# ----------------------------------------------------
# SAĞ SÜTUN: Aktivite Seçimi ve Öneriler
# ----------------------------------------------------
with col_right:
    st.subheader("🎯 Bugünü Planla")
    st.caption("Gitmek istediğin aktiviteye tıkla, lokasyonlar haritaya gelsin:")

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("🏖️ PLAJ / DENİZ", use_container_width=True):
            st.session_state['active_activity'] = "Plaj"
        if st.button("🏄‍♂️ RÜZGAR SÖRFLÜ", use_container_width=True):
            st.session_state['active_activity'] = "Sörf"
        if st.button("⛵ YELKENLİ", use_container_width=True):
            st.session_state['active_activity'] = "Yelkenli"

    with act_col2:
        if st.button("🥾 DOĞA YÜRÜYÜŞÜ", use_container_width=True):
            st.session_state['active_activity'] = "Yürüyüş"
        if st.button("🏛️ TARİHİ GEZİ", use_container_width=True):
            st.session_state['active_activity'] = "Tarih"
        if st.button("🚴 BİSİKLET", use_container_width=True):
            st.session_state['active_activity'] = "Bisiklet"

    secilen_act = st.session_state['active_activity']
    st.success(f"**Seçilen Aktivite:** {secilen_act}")

    # Öneri Detaylarını Gösterme
    st.markdown("---")
    st.subheader("💡 Önerilen Mekanlar")
    
    # Seçilen şehirlerden ilki veya varsayılan İzmir bazlı öneriler
    odak_sehir = secilen_sehirler[0] if secilen_sehirler else "İzmir"
    mekanlar = CITY_ACTIVITIES.get(odak_sehir, {}).get(secilen_act, DEFAULT_SPOTS.get(secilen_act, []))

    for m in mekanlar:
        st.markdown(f"📍 **{m['isim']}**")
        st.caption(f"{m['detay']}")
        st.markdown("---")

# ----------------------------------------------------
# SOL SÜTUN: Dinamik Hava İstatistikleri ve Grafik
# ----------------------------------------------------
with col_left:
    st.subheader(f"Bölgesel Hava ({secilen_tarih.strftime('%d.%m.%Y')})")

    if secilen_sehirler:
        card_cols = st.columns(min(len(secilen_sehirler), 3))
        for idx, sehir in enumerate(secilen_sehirler):
            data = EGE_SEHIRLERI[sehir]
            # Tarihe göre sıcaklık sapması üretme
            gun_sicaklik = data["base_temp"] + (tarih_tohumu % 5) - 2
            with card_cols[idx % 3]:
                st.metric(label=sehir, value=f"{gun_sicaklik}°C", delta=f"{data['durum']}")
                st.caption(f"💧 {data['nem']} | 💨 {data['ruzgar']}")
    else:
        st.warning("Lütfen sol menüden şehir seçiniz.")

    st.markdown("---")
    st.subheader("Haftalık Sıcaklık Grafiği")
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    
    chart_data = {}
    for sehir in secilen_sehirler:
        base = EGE_SEHIRLERI[sehir]["base_temp"]
        chart_data[sehir] = [base + np.sin(i + tarih_tohumu) * 3 for i in range(7)]
    
    df_chart = pd.DataFrame(chart_data, index=gunler)
    st.line_chart(df_chart)

# ----------------------------------------------------
# ORTA SÜTUN: Google Maps Harita
# ----------------------------------------------------
with col_mid:
    st.subheader(" Harita ve Öneri Lokasyonları")

    map_points = []

    # 1. Şehir Merkezleri
    for sehir in secilen_sehirler:
        info = EGE_SEHIRLERI[sehir]
        map_points.append({
            "İsim": f"Şehir Merkezi: {sehir}",
            "lat": info["lat"],
            "lon": info["lon"],
            "Kategori": "Şehir Merkezi",
            "Boyut": 10
        })

    # 2. Seçilen Aktivitenin Şehirdeki Özel Lokasyonları
    for sehir in secilen_sehirler:
        act_spots = CITY_ACTIVITIES.get(sehir, {}).get(secilen_act, DEFAULT_SPOTS.get(secilen_act, []))
        for spot in act_spots:
            map_points.append({
                "İsim": f"📌 {spot['isim']}",
                "lat": spot["lat"],
                "lon": spot["lon"],
                "Kategori": f"Aktivite: {secilen_act}",
                "Boyut": 16
            })

    df_map = pd.DataFrame(map_points)

    if not df_map.empty:
        fig_map = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            hover_name="İsim",
            color="Kategori",
            size="Boyut",
            zoom=6.8,
            center={"lat": 38.0, "lon": 27.8},
            mapbox_style="carto-positron"
        )
        fig_map.update_layout(height=550, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

# 6. ALT ŞERİT
st.markdown("---")
st.info("💡 **İpucu:** Sağ taraftaki butonlara basarak haritada o aktivitenin yapıldığı popüler noktaları anında görüntüleyebilirsiniz.")
