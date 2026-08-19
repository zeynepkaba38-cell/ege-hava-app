import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# 1. Sayfa Ayarları ve Tema
st.set_page_config(
    page_title="EgeHava - Ege Bölgesi Akıllı Hava ve Aktivite Rehberi",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Canlı ve Enerjik CSS Tasarımı
st.markdown("""
<style>
    .main { background-color: #f0f8ff; }
    
    /* Canlı Metric Kartları */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #e6f2ff 100%);
        border: 2px solid #0080ff;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 10px rgba(0, 128, 255, 0.15);
    }
    
    /* Canlı Butonlar */
    .stButton>button {
        background: linear-gradient(90deg, #00b4db 0%, #0083b0 100%);
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff8c00 0%, #ff4500 100%);
        transform: scale(1.03);
    }
    
    /* Aktivite Kartları */
    .spot-card {
        background: white;
        padding: 12px;
        border-left: 5px solid #ff7f50;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# 2. ŞEHİR BAZLI DETAYLI MEKAN VERİ TABANI (Tüm Plajlar & Aktiviteler)
CITY_ACTIVITIES = {
    "İzmir": {
        "Plaj": [
            {"isim": "Ilıca Plajı (Çeşme)", "lat": 38.3075, "lon": 26.3683, "detay": "Sıcak termal kaynak suları, sığ ve altın sarısı kum."},
            {"isim": "Altınkum Plajı (Çeşme)", "lat": 38.2612, "lon": 26.3450, "detay": "Buz gibi berrak denizi ve serinletici rüzgarı."},
            {"isim": "Pırlanta Plajı (Çeşme)", "lat": 38.3180, "lon": 26.2250, "detay": "Rüzgarı ve dalgasıyla ünlü geniş kumsal."},
            {"isim": "Ayayorgi Koyu (Çeşme)", "lat": 38.3360, "lon": 26.3050, "detay": "Durgun denizi ve beach club tesisleri."},
            {"isim": "Akkum Plajı (Seferihisar)", "lat": 38.1961, "lon": 26.8378, "detay": "Mavi bayraklı, rüzgar sörfüne uygun berrak koy."},
            {"isim": "Ekmeksiz Koyu (Seferihisar)", "lat": 38.1880, "lon": 26.8290, "detay": "Çam ormanlarıyla çevrili büyüleyici doğa."},
            {"isim": "Eski Foça Önok Plajı / Halk Plajı", "lat": 38.6710, "lon": 26.7580, "detay": "Tarihi taş evler manzaralı sakin deniz."},
            {"isim": "Sazlıca Koyu (Foça)", "lat": 38.6320, "lon": 26.7620, "detay": "Kamp ve dalış için harika çakıllı berrak koy."},
            {"isim": "Kalem Adası / Akvaryum Koyu (Dikili)", "lat": 39.0080, "lon": 26.7910, "detay": "Maldivler'i aratmayan turkuaz sular."},
            {"isim": "Bademli Halk Plajı (Dikili)", "lat": 39.0180, "lon": 26.8050, "detay": "Zeytin ağaçları arasında doğal akvaryum."},
            {"isim": "Demircili Koyu (Urla)", "lat": 38.2450, "lon": 26.7120, "detay": "Rüzgardan korunaklı dalış ve yüzme noktası."},
            {"isim": "Melengeç Koyu (Urla)", "lat": 38.2510, "lon": 26.6980, "detay": "Sakinlik arayanlar için huzurlu koy."}
        ],
        "Sörf": [
            {"isim": "Alaçatı Sörf Merkezi", "lat": 38.2520, "lon": 26.3768, "detay": "Dünyaca ünlü rüzgar sörfü ve kiteboard okulları."},
            {"isim": "Pırlanta Plajı Kitesurf", "lat": 38.3180, "lon": 26.2250, "detay": "Dalga sörfü ve uçurtma sörfü alanı."},
            {"isim": "Urla Gülbahçe Sörf Koyu", "lat": 38.3320, "lon": 26.6550, "detay": "Sığ suları ile kiteboard öğrenmek için ideal."}
        ],
        "Yelkenli": [
            {"isim": "Urla Marina & Çeşmealtı", "lat": 38.3601, "lon": 26.7725, "detay": "Yelken kulüpleri ve yat turları merkezi."},
            {"isim": "Setur Çeşme Marina", "lat": 38.3250, "lon": 26.3010, "detay": "Uluslararası standartlarda marina ve yelken rotaları."},
            {"isim": "Levent Marina (Balçova)", "lat": 38.4080, "lon": 27.0650, "detay": "İzmir körfez içi yelken turları."}
        ],
        "Yürüyüş": [
            {"isim": "Balçova Terapi Ormanı & Manastır", "lat": 38.3750, "lon": 27.0420, "detay": "Şelale sesleri eşliğinde çam ormanı yürüyüşü."},
            {"isim": "Yamanlar Dağı & Karagöl", "lat": 38.5550, "lon": 27.2110, "detay": "Kışın krater gölü etrafında harika doğa parkuru."},
            {"isim": "Kozak Yaylası (Bergama)", "lat": 39.2150, "lon": 26.9850, "detay": "Fıstık çamları arasında temiz hava yürüyüşü."},
            {"isim": "Nif Dağı Yürüyüş Rotaları (Kemalpaşa)", "lat": 38.3810, "lon": 27.3820, "detay": "Zorlu doğa ve dağ tırmanış kulvarı."}
        ],
        "Tarih": [
            {"isim": "Efes Antik Kenti (Selçuk)", "lat": 37.9485, "lon": 27.3680, "detay": "Dünya mirası UNESCO antik kenti ve Celsus Kütüphanesi."},
            {"isim": "Bergama Acropolis", "lat": 39.1320, "lon": 27.1840, "detay": "Dik tiyatrosu ve antik tapınakları ile muazzam tepe."},
            {"isim": "Smyrna Agora Antik Kenti (Konak)", "lat": 38.4180, "lon": 27.1380, "detay": "Tarihi Kemeraltı merkezindeki Roma agorası."},
            {"isim": "Çeşme Kalesi & Müzesi", "lat": 38.3240, "lon": 26.3030, "detay": "Osmanlı dönemi deniz kalesi."}
        ],
        "Bisiklet": [
            {"isim": "Kordon Boyu - Bostanlı Sahil Şeridi", "lat": 38.4350, "lon": 27.1380, "detay": "Kesintisiz 15 km düz deniz kenarı bisiklet yolu."},
            {"isim": "İnciraltı Kent Ormanı", "lat": 38.4110, "lon": 27.0350, "detay": "Ağaçlar altında ve lagün çevresinde sürüş."},
            {"isim": "Urla Bağ Yolu Bisiklet Rotası", "lat": 38.3120, "lon": 26.7520, "detay": "Doğa ve gastronomi temalı bisiklet turu."}
        ]
    },
    "Muğla": {
        "Plaj": [
            {"isim": "Ölüdeniz Belcekız & Lagün", "lat": 36.5492, "lon": 29.1165, "detay": "Dünyaca ünlü durgun turkuaz lagün."},
            {"isim": "Iztuzu Plajı (Dalyan)", "lat": 36.7905, "lon": 28.6180, "detay": "Caretta caretta kaplumbağaları koruma alanı."},
            {"isim": "Kelebekler Vadisi Koyu", "lat": 36.4980, "lon": 29.1280, "detay": "Sarp kayalıklar ortasında saklı cennet."},
            {"isim": "Kabak Koyu (Fethiye)", "lat": 36.4620, "lon": 29.1250, "detay": "Bohem atmosferi ve bakir doğasıyla koy."},
            {"isim": "Palamutbükü Plajı (Datça)", "lat": 36.6780, "lon": 27.5020, "detay": "Akvaryum kadar berrak taşlı deniz."},
            {"isim": "Bitez Plajı (Bodrum)", "lat": 37.0280, "lon": 27.3850, "detay": "Sığ ve aileler için ideal Bodrum sahil."}
        ],
        "Sörf": [{"isim": "Akyaka Kitesurf Plajı", "lat": 37.0520, "lon": 28.3220, "detay": "Dünyanın en iyi uçurtma sörfü rüzgarı."}],
        "Yelkenli": [{"isim": "Göcek Marinaları", "lat": 36.7560, "lon": 28.9380, "detay": "Mavi yolculuk başlangıç merkezi."}],
        "Yürüyüş": [{"isim": "Likya Yolu Başlangıcı", "lat": 36.5750, "lon": 29.1430, "detay": "Dünyanın en güzel 10 yürüyüş rotasından biri."}],
        "Tarih": [{"isim": "Bodrum Kalesi", "lat": 37.0315, "lon": 27.4295, "detay": "Sualtı arkeoloji müzesi."}],
        "Bisiklet": [{"isim": "Marmaris Yalancıboğaz", "lat": 36.8180, "lon": 28.2950, "detay": "Çam kokulu orman sürüşü."}]
    },
    "Aydın": {
        "Plaj": [
            {"isim": "Altınkum Plajı (Didim)", "lat": 37.3565, "lon": 27.2830, "detay": "Sığ ve altın kumlu sahil."},
            {"isim": "Kadınlar Denizi (Kuşadası)", "lat": 37.8420, "lon": 27.2480, "detay": "Kuşadası şehir içi plajı."},
            {"isim": "Sevgi Plajı (Davutlar)", "lat": 37.7520, "lon": 27.2610, "detay": "Okaliptüs ağaçları altında uzun kumsal."}
        ],
        "Yürüyüş": [{"isim": "Dilek Yarımadası Milli Parkı", "lat": 37.6710, "lon": 27.1650, "detay": "Kanyon ve koy yürüyüşü."}],
        "Tarih": [{"isim": "Didim Apollon Tapınağı", "lat": 37.3850, "lon": 27.2560, "detay": "Devasa kehanet tapınağı."}],
        "Sörf": [{"isim": "Kuşadası Sevgi Plajı Spor Alanı", "lat": 37.7850, "lon": 27.2600, "detay": "Rüzgar aktiviteleri."}],
        "Yelkenli": [{"isim": "Kuşadası Setur Marina", "lat": 37.8680, "lon": 27.2610, "detay": "Yat rotaları."}],
        "Bisiklet": [{"isim": "Bafa Gölü Kıyı Yolu", "lat": 37.5020, "lon": 27.4200, "detay": "Tarihi kaya resimleri rotası."}]
    }
}

DEFAULT_SPOTS = {
    "Plaj": [{"isim": "Bölge Sahil Şeridi", "lat": 38.0, "lon": 27.5, "detay": "Doğal sahil alanı."}],
    "Yürüyüş": [{"isim": "Kent Tabiat Parkı", "lat": 38.5, "lon": 28.0, "detay": "Orman yürüyüşü."}],
    "Tarih": [{"isim": "Kent Müzesi", "lat": 38.8, "lon": 29.0, "detay": "Tarihi mekanlar."}],
    "Sörf": [{"isim": "Rüzgar Alan Sahil", "lat": 38.2, "lon": 26.8, "detay": "Su sporları alanı."}],
    "Yelkenli": [{"isim": "Liman Parkı", "lat": 37.9, "lon": 27.2, "detay": "Tekne iskelesi."}],
    "Bisiklet": [{"isim": "Şehir Bisiklet Parkuru", "lat": 38.6, "lon": 27.4, "detay": "Güvenli sürüş kulvarı."}]
}

# Ege Bölgesi Şehir Temel Verileri
EGE_SEHIRLERI = {
    "İzmir": {"lat": 38.4237, "lon": 27.1428, "base_temp": 31, "durum_yaz": "Güneşli", "durum_kis": "Yağmurlu / Ilık", "nem": "%45", "ruzgar": "20 km/h NW"},
    "Aydın": {"lat": 37.8560, "lon": 27.8416, "base_temp": 33, "durum_yaz": "Açık / Sıcak", "durum_kis": "Bulutlu", "nem": "%40", "ruzgar": "18 km/h N"},
    "Muğla": {"lat": 37.2153, "lon": 28.3636, "base_temp": 29, "durum_yaz": "Güneşli", "durum_kis": "Sağanak Yağışlı", "nem": "%49", "ruzgar": "22 km/h NW"},
    "Manisa": {"lat": 38.6191, "lon": 27.4289, "base_temp": 32, "durum_yaz": "Az Bulutlu", "durum_kis": "Sisli / Soğuk", "nem": "%42", "ruzgar": "15 km/h NE"},
    "Denizli": {"lat": 37.7765, "lon": 29.0864, "base_temp": 30, "durum_yaz": "Sıcak", "durum_kis": "Parçalı Bulutlu", "nem": "%38", "ruzgar": "12 km/h E"},
    "Kütahya": {"lat": 39.4167, "lon": 29.9833, "base_temp": 26, "durum_yaz": "Parçalı Bulutlu", "durum_kis": "Kar Yağışlı", "nem": "%55", "ruzgar": "14 km/h W"},
    "Uşak": {"lat": 38.6823, "lon": 29.4082, "base_temp": 27, "durum_yaz": "Açık", "durum_kis": "Soğuk / Rüzgarlı", "nem": "%50", "ruzgar": "16 km/h NW"},
    "Afyonkarahisar": {"lat": 38.7507, "lon": 30.5567, "base_temp": 25, "durum_yaz": "Az Bulutlu", "durum_kis": "Karlı / Ayaz", "nem": "%58", "ruzgar": "19 km/h NE"}
}

# 3. SOL YAN MENÜ (Logo & Ayarlar)
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 15px;">
    <svg width="80" height="80" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="35" fill="#ff8c00" />
        <path d="M 15 65 Q 35 50 50 65 T 85 65 L 85 85 L 15 85 Z" fill="#00b4db" opacity="0.8"/>
        <path d="M 15 75 Q 35 60 50 75 T 85 75 L 85 85 L 15 85 Z" fill="#0083b0"/>
    </svg>
    <h2 style="color:#0083b0; margin-top:0;">EgeHava</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Görünüm Ayarları")
st.sidebar.markdown("---")

# İstatistik Gösterge Seçimleri
goster_sicaklik = st.sidebar.checkbox("🌡️ Sıcaklığı Göster", value=True)
goster_nem = st.sidebar.checkbox("💧 Nem Oranını Göster", value=True)
goster_ruzgar = st.sidebar.checkbox("💨 Rüzgar Bilgisini Göster", value=True)

st.sidebar.markdown("---")
secilen_sehirler = st.sidebar.multiselect(
    "Görüntülenecek Şehirler:",
    options=list(EGE_SEHIRLERI.keys()),
    default=["İzmir", "Muğla", "Aydın"]
)

# 4. ÜST BAŞLIK & DİNAMİK TARİH (ARALIK & TÜM AYLAR ÇALIŞIR)
header_col1, header_col2 = st.columns([3, 1.2])
with header_col1:
    st.title("🌤️ EgeHava — Akıllı Hava & Aktivite Rehberi")
with header_col2:
    secilen_tarih = st.date_input("📅 Tarih Seçimi", value=datetime.date.today())

# Mevsimsel Sıcaklık ve Durum Hesabı (Aralık / Kış Desteği)
ay = secilen_tarih.month
is_kis = ay in [12, 1, 2]
is_bahar = ay in [3, 4, 5, 9, 10, 11]

if is_kis:
    temp_modifier = -18
    mevsim_adi = "Kış"
elif is_bahar:
    temp_modifier = -8
    mevsim_adi = "Bahar"
else:
    temp_modifier = 0
    mevsim_adi = "Yaz"

tarih_tohumu = secilen_tarih.day + ay * 30

st.markdown("---")

# 5. ANA PANEL
col_left, col_mid, col_right = st.columns([1.3, 1.3, 1.1])

if 'active_activity' not in st.session_state:
    st.session_state['active_activity'] = "Plaj"

# ----------------------------------------------------
# SAĞ SÜTUN: Aktivite Seçimi ve Sınırsız Öneriler
# ----------------------------------------------------
with col_right:
    st.subheader("🎯 Bugünü Planla")
    st.caption(f"**Mevsim:** {mevsim_adi} | Aktiviteye tıkla, tüm lokasyonlar haritaya gelsin:")

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

    # Kış Ayı Özel Uyarı & Tavsiyesi
    if is_kis and secilen_act in ["Plaj", "Sörf"]:
        st.warning("❄️ **Kış Mevsimi Uyarısı:** Deniz suyu soğuktur. Yüzmek yerine kordon yürüyüşü, deniz manzaralı kafeler veya termal tesisler önerilir!")

    st.markdown("---")
    st.subheader(f"💡 Önerilen Tüm Mekanlar ({len(CITY_ACTIVITIES.get(secilen_sehirler[0] if secilen_sehirler else 'İzmir', {}).get(secilen_act, []))} Mekan)")

    odak_sehir = secilen_sehirler[0] if secilen_sehirler else "İzmir"
    mekanlar = CITY_ACTIVITIES.get(odak_sehir, {}).get(secilen_act, DEFAULT_SPOTS.get(secilen_act, []))

    # Tüm Mekanları Listeleme
    for m in mekanlar:
        st.markdown(f"""
        <div class="spot-card">
            <b>📍 {m['isim']}</b><br>
            <small style="color: #555;">{m['detay']}</small>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# SOL SÜTUN: Hava Durumu (Aralık Uyumlu)
# ----------------------------------------------------
with col_left:
    st.subheader(f"Bölgesel Hava ({secilen_tarih.strftime('%d %B %Y')})")

    if secilen_sehirler:
        card_cols = st.columns(min(len(secilen_sehirler), 2))
        for idx, sehir in enumerate(secilen_sehirler):
            data = EGE_SEHIRLERI[sehir]
            
            # Dinamik Sıcaklık Hesabı
            gun_sicaklik = max(-3, data["base_temp"] + temp_modifier + (tarih_tohumu % 4) - 2)
            durum = data["durum_kis"] if is_kis else data["durum_yaz"]

            with card_cols[idx % 2]:
                val_text = f"{gun_sicaklik}°C" if goster_sicaklik else "---"
                st.metric(label=sehir, value=val_text, delta=f"{durum}")
                
                info_line = ""
                if goster_nem: info_line += f"💧 {data['nem']} "
                if goster_ruzgar: info_line += f"| 💨 {data['ruzgar']}"
                st.caption(info_line)
    else:
        st.warning("Lütfen sol menüden en az bir şehir seçiniz.")

    st.markdown("---")
    st.subheader("Haftalık Trend Grafiği")
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    
    chart_data = {}
    for sehir in secilen_sehirler:
        base = EGE_SEHIRLERI[sehir]["base_temp"] + temp_modifier
        chart_data[sehir] = [base + np.sin(i + tarih_tohumu) * 2 for i in range(7)]
    
    df_chart = pd.DataFrame(chart_data, index=gunler)
    st.line_chart(df_chart)

# ----------------------------------------------------
# ORTA SÜTUN: Harita ve Özel Pinler
# ----------------------------------------------------
with col_mid:
    st.subheader("📍 Lokasyon Haritası")

    map_points = []

    # Şehir Merkezleri
    for sehir in secilen_sehirler:
        info = EGE_SEHIRLERI[sehir]
        map_points.append({
            "İsim": f"Şehir Merkezi: {sehir}",
            "lat": info["lat"],
            "lon": info["lon"],
            "Kategori": "Şehir Merkezi",
            "Boyut": 10
        })

    # Seçilen Aktivitenin Tüm Lokasyonları
    for sehir in secilen_sehirler:
        act_spots = CITY_ACTIVITIES.get(sehir, {}).get(secilen_act, DEFAULT_SPOTS.get(secilen_act, []))
        for spot in act_spots:
            map_points.append({
                "İsim": f"📌 {spot['isim']}",
                "lat": spot["lat"],
                "lon": spot["lon"],
                "Kategori": f"{secilen_act} Noktaları",
                "Boyut": 15
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
            center={"lat": 38.2, "lon": 27.2},
            mapbox_style="carto-positron",
            color_discrete_sequence=["#0083b0", "#ff4500", "#ff8c00"]
        )
        fig_map.update_layout(height=580, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.info("✨ **Güncelleme Başarılı:** Tüm aylar (Aralık dahil), kış/yaz aktivite ve canlı mekan önerileri aktifleştirildi.")
