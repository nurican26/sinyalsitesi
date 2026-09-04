# 1. Sayfa Yapılandırması ve Yenilenen Işıklı/Gölgeli Tasarım
st.set_page_config(page_title="BTA", page_icon="📈", layout="wide")

st.markdown('''
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)!important; 
    padding: 0.5rem;
} 
h1,h2,h3,h4,h5,h6,p,span,label {
    color: #fff!important; 
    font-family: "Segoe UI", sans-serif;
} 
input {
    color: #000!important; 
    background-color: #fff!important;
} 
.stDataFrame {
    width: 100% !important; 
    border: 1px solid #10b981 !important; 
    border-radius: 8px;
} 
div.block-container {
    padding-top: 1rem; 
    padding-bottom: 0.5rem;
} 
.alsat-baslik {
    background: linear-gradient(90deg, #ca8a04 0%, #1e1b4b 100%); 
    padding: 8px; 
    border-radius: 5px; 
    font-weight: bold; 
    margin-bottom: 5px;
} 
.al-baslik {
    background: linear-gradient(90deg, #16a34a 0%, #1e1b4b 100%); 
    padding: 8px; 
    border-radius: 5px; 
    font-weight: bold; 
    margin-bottom: 5px;
} 

/* ✨ GÜNCELLENEN EL YAZISI, PARLAK VE ALTINDAN GÖLGELİ BTA */
.bta-logo-konteyner {
    display: flex; 
    justify-content: center; 
    align-items: center; 
    margin-top: 25px; 
    margin-bottom: 35px;
    width: 100%;
    background: transparent !important; /* Arkası tamamen boş */
} 
.bta-logo-yazi {
    font-family: "Brush Script MT", "Comic Sans MS", cursive, sans-serif !important; 
    font-size: 5rem !important; 
    font-weight: bold !important; 
    color: #00f0ff !important; /* Canlı ve parlayan yeni cyan/mavi rengi */
    text-align: center;
    position: relative;
    
    /* Yazının kendi parlaklık ışığı ve hemen altındaki siyah derinlik gölgesi */
    text-shadow: 
        0 0 10px #00f0ff,
        0 0 20px #00f0ff,
        3px 8px 10px rgba(0, 0, 0, 0.8); 
}
</style>
''', unsafe_allow_html=True)
