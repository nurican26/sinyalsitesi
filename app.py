with st.spinner("Excel verileri işleniyor..."):
            tablo_verisi = []
            sutun_sayisi = len(df_kaynak.columns)
            for i in range(2, len(df_kaynak)):
                try:
                    if sutun_sayisi > 20:
                        # Hücre verisini güvenli bir şekilde string'e çeviriyoruz
                        raw_val = df_kaynak.iloc[i, 20]
                        if pd.isna(raw_val): # Excel'deki boş hücreleri (NaN) güvenli yakalama
                            continue
                            
                        u_val = str(raw_val).strip().upper()
                        
                        # 121. Satır Hata Koruması: Geçersiz veya başlık metinlerini atla
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
                                # 136. Satır Hata Koruması: Liste boşsa hata vermemesi için ilk eleman kontrolü
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
                except Exception as e:
                    pass # Tek bir satırdaki bozuk veri tüm döngüyü ve uygulamayı kilitlemesin diye koruma
