# ===================================================================== #
# 3. ANA VERİ MOTORU VE TABLOLAR (DİKEY DÜZEN - BİLGİLER KORUNDU)
# ===================================================================== #
st.write("---")
if os.path.exists(excel_yolu):
    try:
        df = pd.read_excel(excel_yolu, sheet_name="WEB", engine="openpyxl")
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#1E90FF;">📈 BTA ALGORİTMİK HİSSE </p>', unsafe_allow_html=True)
        veri_var_mi = False
        
        # Yatay tablo yerine bilgileri dikey kart şeklinde basıyoruz
        for idx in range(min(10, len(df))):
            ha = str(df.iloc[idx, 0]).strip().upper() if pd.notna(df.iloc[idx, 0]) else ""
            alim_c = str(df.iloc[idx, 2]).strip() if pd.notna(df.iloc[idx, 2]) else ""
            puan_d = df.iloc[idx, 3]
            
            if ha != "" and ha not in ["BTA HİSSE", "HİSSE", "NAN", "NONE", "ANA", "RAYSG"]:
                veri_var_mi = True
                if isinstance(puan_d, (int, float)):
                    p_temiz = f"{float(puan_d):.2f}"
                else:
                    p_temiz = str(puan_d).strip()
                    
                h_veri = yf.Ticker(f"{ha}.IS").history(period="1d", timeout=2)
                if len(h_veri) > 0:
                    c_fiyat = float(h_veri['Close'].iloc[-1])
                else:
                    c_fiyat = 0.0
                
                alim_c_temiz = alim_c.replace(",", ".")
                if alim_c_temiz.replace(".", "", 1).isdigit():
                    maliyet = float(alim_c_temiz)
                else:
                    maliyet = 0.0
                
                if maliyet > 0 and c_fiyat > 0:
                    or_dg = ((c_fiyat - maliyet) / maliyet) * 100
                    if or_dg >= 0:
                        kz_str = f'<span style="color:#00ff66;">▲ %{or_dg:.2f}</span>'
                    else:
                        kz_str = f'<span style="color:#ff3344;">▼ %{or_dg:.2f}</span>'
                else:
                    kz_str = "<span>-</span>"
                
                # Dikey Bilgi Kartı Tasarımı
                dikey_kart_html = f'''
                <div style="background-color: #121d33; border: 1px solid #1e3a5f; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                    <div style="font-size: 18px; color: #00ffcc; border-bottom: 1px solid #1e2e4d; padding-bottom: 5px; margin-bottom: 10px; font-weight: bold;">📍 {ha} HİSSE BİLGİLERİ</div>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 15px; color: #ffffff;">
                        <div><b>BTA PUANI:</b> <span style="color: #00ffcc;">{p_temiz}</span></div>
                        <div><b>ALGORİTMİK FİYATI:</b> {maliyet:,.2f} TL</div>
                        <div><b>FİYAT:</b> {c_fiyat:,.2f} TL</div>
                        <div><b>K/Z:</b> {kz_str}</div>
                    </div>
                </div>
                '''
                st.markdown(dikey_kart_html, unsafe_allow_html=True)
        
        # --- BORSA ARAMA MOTORU ---
        st.markdown('<p style="font-size:18px; font-weight:bold; color:#FFA500;">🔍 BIST HİSSE ARAMA MOTORU</p>', unsafe_allow_html=True)
        if len(df.columns) >= 5:
            tum_hisseler = sorted([str(h).strip().upper() for h in df.iloc[:, 4].dropna().unique() if str(h).strip().upper() not in ["HİSSE", "HİSSELER", ""]])
            if tum_hisseler:
                aranan_hisse = st.selectbox("Hisse seçin", ["Seçiniz..."] + tum_hisseler)
                if aranan_hisse != "Seçiniz...":
                    h_detay_veri = yf.Ticker(f"{aranan_hisse}.IS").history(period="1d", timeout=2)
                    if len(h_detay_veri) > 0:
                        st.metric("Güncel Fiyat", f"{float(h_detay_veri['Close'].iloc[-1]):,.2f} TL")
    except:
        pass
else:
    st.error("Excel bulunamadı.")
