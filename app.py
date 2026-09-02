# 🟡 1. ADIM: SARI BUTON
    if al_sat_butonu and df_kaynak is not None:
        with st.spinner("Excel verileri işleniyor..."):
            tablo_verisi = []
            sutun_sayisi = len(df_kaynak.columns)
            for i in range(2, len(df_kaynak)):
                try:
                    if sutun_sayisi > 20:
                        raw_val = df_kaynak.iloc[i, 20]
                        if pd.isna(raw_val): 
                            continue
                            
                        u_val = str(raw_val).strip().upper()
                        if not u_val or any(x in u_val for x in ["NAN", "AL SAT SİNYALİ", "AL_SAT SİNYALİ", ""]):
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
                                yuklenen_fiy = float(sayilar) if sayilar else 0.0
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
    elif al_sat_butonu and df_kaynak is None:
        st.warning("Lütfen önce geçerli bir Excel dosyası yükleyin.")

    # 🟢 2. ADIM: YEŞİL BUTON
    if al_butonu and df_kaynak is not None:
        with st.spinner("AL sinyalleri hesaplanıyor..."):
            tablo_verisi_al = []
            sutun_sayisi = len(df_kaynak.columns)
            for i in range(2, len(df_kaynak)):
                try:
                    if sutun_sayisi > 22:
                        raw_w = df_kaynak.iloc[i, 22]
                        if pd.isna(raw_w):
                            continue
                            
                        w_val = str(raw_w).strip().upper()
                        if not w_val or any(x in w_val for x in ["NAN", "AL", ""]):
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
    elif al_butonu and df_kaynak is None:
        st.warning("Lütfen önce geçerli bir Excel dosyası yükleyin.")

    st.divider()

    # 💬 TOPLULUK SOHBET ODASI
    st.subheader("💬 Topluluk Sohbet Odası")
    with st.form("mesaj_formu", clear_on_submit=True):
        kullanici_mesaji = st.text_input("Mesajınızı yazın:", placeholder="Buraya yazın...")
        mesaj_gonder = st.form_submit_button("Gönder", use_container_width=True)
        
        if mesaj_gonder and kullanici_mesaji:
            mesaj_temiz = kullanici_mesaji.lower()
            if any(kufur in mesaj_temiz for kufur in st.session_state["engellenen_kelimeler"]):
                st.error("⚠️ Mesajınız uygunsuz kelimeler içerdiği için engellendi.")
            else:
                zaman = datetime.datetime.now().strftime("%H:%M")
                st.session_state["chat_history"].insert(0, f"[{zaman}] Kullanıcı: {kullanici_mesaji}")
                st.rerun()

    if st.session_state["chat_history"]:
        for msg in st.session_state["chat_history"]:
            st.write(msg)
    else:
        st.info("Henüz mesaj yazılmamış. İlk mesajı siz yazın!")

# ------------------------------------------
# 🎯 SAĞ TARAF: CANLI TAKİP & OYLAMA PANELİ
# ------------------------------------------
with sag_taraf:
    st.subheader("🎯 Canlı Takip")
    
    # ⚡ TÜM HİSSELERE AİT SABİT CANLI KÖŞE
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
            st.dataframe(pd.DataFrame(canli_borsa_listesi), use_container_width=True, hide_index=True, height=250)
        else:
            st.error("Borsa canlı verileri şu anda çekilemedi.")

    st.divider()

    # 🌟 SİNYAL HAVUZUNA ALINAN HİSSELER
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
                pass
        
        if takip_listesi:
            st.dataframe(pd.DataFrame(takip_listesi), use_container_width=True, hide_index=True)
            if st.button("🗑️ Takip Listesini Temizle", use_container_width=True):
                st.session_state["ozel_takip_kutusu"] = {}
                st.rerun()
    else:
        st.info("Henüz takibe alınan dinamik bir hisse bulunmuyor.")

    st.divider()

    # ⭐ EN ALTA EKLENEN PUANLAMA VE BEĞENİ SİSTEMİ
    st.markdown("#### 🗳️ Paneli Değerlendir")
    with st.form("oylama_formu", clear_on_submit=True):
        secilen_puan = st.slider("Panele Yıldız Verin (1-5):", min_value=1, max_value=5, value=5, step=1)
