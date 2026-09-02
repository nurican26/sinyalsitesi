# ==========================================
# 📊 HERKESİN GÖRECEĞİ BEĞENİ VE POPÜLARİTE VİTRİNİ
# ==========================================
ortalama_puan = st.session_state["topham_yildiz_puani"] / st.session_state["topham_oy_sayisi"] if st.session_state["topham_oy_sayisi"] > 0 else 0.0

col_vitrin1, col_vitrin2 = st.columns(2)
with col_vitrin1:
    st.metric(label="🔥 Toplam Panel Beğenisi (Oy)", value=f"{st.session_state['topham_oy_sayisi']} Kişi")
with col_vitrin2:
    st.metric(label="⭐ Topluluk Puan Ortalaması", value=f"{ortalama_puan:.2f} / 5.0")

guncel_an = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
st.success(f"💡 Sistem Aktif. Son Panel Yenilenme Zamanı: {guncel_an}")

st.markdown("<div style='background-color: rgba(220, 38, 38, 0.15); border-left: 5px solid #dc2626; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><p style='margin: 0; font-weight: bold; color: #f87171 !important;'>⚠️ SPK YASAL UYARI: Yatırım tavsiyesi değildir.</p></div>", unsafe_allow_html=True)

# 📂 Excel Dosya Yükleme
st.markdown("### 📁 Güncel Excel Dosyası Yükleme")
yuklenen_dosya = st.file_uploader("Excel dosyasını seçin (.xlsx, .xlsm)", type=["xlsx", "xlsm"])

df_kaynak = None
if yuklenen_dosya is not None:
    try:
        df_kaynak = pd.read_excel(yuklenen_dosya, sheet_name=0, header=None)
        st.info("🔒 Excel dosyası güvenli bellek üzerinde işlendi.")
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
elif os.path.exists(DEFAULT_EXCEL_PATH):
    try:
        df_kaynak = pd.read_excel(DEFAULT_EXCEL_PATH, header=None)
    except:
        pass

BORSA_HISSELERI = ["RAYSG", "SONME", "ZEDUR", "DOCO", "LYDYE", "MRSHL", "CMBTN", "UFUK", "GUNDG", "MAALT", "VERUS", "ALCAR", "AYCES", "ALKLC", "KAPLM", "INGRM", "FORTE", "PKENT", "DUNYH"]

# ==========================================
# 📊 YAN YANA PANEL DÜZENI (Önce Sütunlar Tanımlanıyor)
# ==========================================
sol_taraf, sag_taraf = st.columns([1.1, 0.9])

# --- SOL TARAF: SİNYAL ÜRETİM MERKEZİ ---
with sol_taraf:
    st.subheader("📈 Sinyal Üretim Merkezi")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        al_sat_butonu = st.button("🟡 AL SAT SİNYALİNİ GÖSTER", use_container_width=True)
    with col_btn2:
        al_butonu = st.button("🟢 AL SİNYALİNİ GÖSTER", use_container_width=True)
        
    # Orijinal Olarak Korunan Sarı Buton Mantığı
    if al_sat_butonu and df_kaynak is not None:
        with st.spinner("Excel verileri işleniyor..."):
            tablo_verisi = []
            sutun_sayisi = len(df_kaynak.columns)
            for i in range(2, len(df_kaynak)):
                try:
                    if sutun_sayisi > 20:
                        u_val = str(df_kaynak.iloc[i, 20]).strip().upper()
                        
                        if not u_val or u_val in ["NAN", "AL SAT SİNYALİ", "AL_SAT SİNYALİ", ""]:
                            continue
                        
                        if "SONME" in u_val or "ALKLC" in u_val:
                            continue
                            
                        hisse_adi = None
                        for h in BORSA_HISSELERI:
                            if h in u_val:
                                hisse_adi = h
                                break
                        
                        if hisse_adi:
                            try:
                                fiyat_str = str(df_kaynak.iloc[i, 7]).replace(",", ".").strip() if sutun_sayisi > 7 else "0"
                                sayilar = re.findall(r"[-+]?\d*\.\d+|\d+", fiyat_str)
                                yuklenen_fiy = float(sayilar[0]) if sayilar else 0.0
                            except:
                                yuklenen_fiy = 0.0
                            
                            hisse_data = yf.Ticker(f"{hisse_adi}.IS").history(period="1d")
                            if not hisse_data.empty:
                                canli_fiyat = hisse_data['Close'].iloc[-1]
                                if yuklenen_fiy == 0.0:
                                    yuklenen_fiy = canli_fiyat
                                    
                                yuzde_fark = ((canli_fiyat - yuklenen_fiy) / yuklenen_fiy) * 100 if yuklenen_fiy > 0 else 0.0
                                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı" if canli_fiyat >= yuklenen_fiy else f"🔴 %{abs(yuzde_fark):.2f} İçeride"
                                tablo_verisi.append({
                                    "Hisse Kodu": hisse_adi, 
                                    "Sinyal Metni": u_val, 
                                    "Yüklenen Fiyat": f"{yuklenen_fiy:.2f} TL", 
                                    "Canlı Fiyat": f"{canli_fiyat:.2f} TL", 
                                    "Durum Oranı": durum_str
                                })
                except:
                    pass
            if tablo_verisi:
                st.dataframe(pd.DataFrame(tablo_verisi), use_container_width=True, hide_index=True)
            else:
                st.warning("Excel şablonunda aktif AL SAT sinyali bulunamadı.")

    # Orijinal Olarak Korunan Yeşil Buton Mantığı
    if al_butonu and df_kaynak is not None:
        with st.spinner("AL sinyalleri hesaplanıyor..."):
            tablo_verisi_al = []
            sutun_sayisi = len(df_kaynak.columns)
            for i in range(2, len(df_kaynak)):
                try:
                    if sutun_sayisi > 22:
                        w_val = str(df_kaynak.iloc[i, 22]).strip().upper()
                        
                        if not w_val or w_val in ["NAN", "AL", ""]:
                            continue
                            
                        hisse_adi = None
                        for h in BORSA_HISSELERI:
                            if h in w_val:
                                hisse_adi = h
                                break
                        
                        if hisse_adi:
                            hisse_data = yf.Ticker(f"{hisse_adi}.IS").history(period="1d")
                            if not hisse_data.empty:
                                canli_fiyat = hisse_data['Close'].iloc[-1]
                                yuklenen_fiy = canli_fiyat 
                                yuzde_fark = 0.0  
                                durum_str = f"🟢 %{yuzde_fark:.2f} Kazandı"
                                
                                st.session_state["ozel_takip_kutusu"][hisse_adi] = {"kayit_fiyati": canli_fiyat, "kayit_zamani": guncel_an}
                                tablo_verisi_al.append({
                                    "Hisse Kodu": hisse_adi, 
                                    "Sinyal": w_val, 
                                    "Yüklenen Fiyat": f"{yuklenen_fiy:.2f} TL", 
                                    "Canlı Fiyat": f"{canli_fiyat:.2f} TL", 
                                    "Durum Oranı": durum_str
                                })
                except:
                    pass
            if tablo_verisi_al:
                st.dataframe(pd.DataFrame(tablo_verisi_al), use_container_width=True, hide_index=True)
            else:
                st.warning("Excel şablonunda aktif AL sinyali bulunamadı.")

# --- SAĞ TARAF: CANLI BORSA KÖŞESİ & TAKİP PANELİ ---
with sag_taraf:
    st.subheader("🎯 Canlı Takip & Topluluk Paneli")
    
    st.markdown("#### ⚡ Tüm Hisseler Canlı Borsa Takip Köşesi")
    with st.spinner("Anlık borsa fiyatları çekiliyor..."):
        canli_borsa_listesi = []
        for hisse in BORSA_HISSELERI:
            try:
                hisse_obj = yf.Ticker(f"{hisse}.IS")
                hisse_data = hisse_obj.history(period="2d")
                if len(hisse_data) >= 2:
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    onceki_kapanis = hisse_data['Close'].iloc[-2]
                    gunluk_degisim = ((guncel_fiy - onceki_kapanis) / onceki_kapanis) * 100
                    
                    canli_borsa_listesi.append({
                        "Hisse Kodu": hisse,
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Günlük Değişim": f"🟢 %+{gunluk_degisim:.2f}" if gunluk_degisim >= 0 else f"🔴 %{gunluk_degisim:.2f}"
                    })
                elif not hisse_data.empty:
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    canli_borsa_listesi.append({
                        "Hisse Kodu": hisse,
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Günlük Değişim": "🔄 Veri Yok"
                    })
            except:
                pass
        
        if canli_borsa_listesi:
            st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=300)
        else:
            st.error("Borsa canlı verileri şu anda çekilemedi.")

    st.divider()

    st.markdown("#### 🌟 Sinyal Havuzuna Alınan Hisseler")
    if st.session_state["ozel_takip_kutusu"]:
        takip_listesi = []
        for hisse, bilgi in list(st.session_state["ozel_takip_kutusu"].items()):
            try:
                hisse_data = yf.Ticker(f"{hisse}.IS").history(period="1d")
                if not hisse_data.empty:
                    guncel_fiy = hisse_data['Close'].iloc[-1]
                    ilkesel_fiy = bilgi["kayit_fiyati"]
                    degisim = ((guncel_fiy - ilkesel_fiy) / ilkesel_fiy) * 100
                    
                    takip_listesi.append({
                        "Hisse Kodu": hisse,
                        "Giriş Fiyatı": f"{ilkesel_fiy:.2f} TL",
                        "Anlık Fiyat": f"{guncel_fiy:.2f} TL",
                        "Performans": f"🟢 %{degisim:.2f}" if degisim >= 0 else f"🔴 %{degisim:.2f}",
                        "Kayıt Zamanı": bilgi["kayit_zamani"]
                    })
            except:
