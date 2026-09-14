from flask import Flask, jsonify, render_template, request
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Varsayılan olarak takip edilecek borsa sembolleri listesi
# BIST hisseleri için sonuna .IS eklenmelidir (Örn: THYAO.IS, EREGL.IS)
WATCHLIST = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "AAPL", "TSLA", "MSFT"]

def fetch_stock_data(ticker_symbol):
    """
    Yahoo Finance API kullanarak tek bir hissenin canlı verilerini çeken fonksiyon.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # En güncel günlük veriyi (1 günlük periyot, 1 dakikalık barlar) çekiyoruz
        todays_data = ticker.history(period="1d", interval="1m")
        
        if todays_data.empty:
            # Eğer bugünün verisi henüz yoksa (piyasa açılmadıysa) son 2 günün verisini kontrol et
            todays_data = ticker.history(period="2d")
            
        if not todays_data.empty:
            # Son kapanış fiyatı (Anlık Fiyat)
            current_price = todays_data['Close'].iloc[-1]
            
            # Günün en yüksek ve en düşük değerleri
            day_high = todays_data['High'].max()
            day_low = todays_data['Low'].min()
            
            # Önceki günün kapanış fiyatını bularak değişim yüzdesini hesaplama
            info = ticker.info
            previous_close = info.get('previousClose', current_price)
            
            price_change = current_price - previous_close
            pct_change = (price_change / previous_close) * 100
            
            # Şirket ismini al, yoksa sembolün kendisini kullan
            company_name = info.get('longName', ticker_symbol)
            
            return {
                "symbol": ticker_symbol,
                "name": company_name,
                "price": round(current_price, 2),
                "change": round(pct_change, 2),
                "high": round(day_high, 2),
                "low": round(day_low, 2),
                "status": "success"
            }
    except Exception as e:
        print(f"Hata oluştu ({ticker_symbol}): {str(e)}")
        
    # Hata durumunda veya veri bulunamadığında döndürülecek şablon
    return {
        "symbol": ticker_symbol,
        "name": "Veri Alınamadı",
        "price": 0.0,
        "change": 0.0,
        "high": 0.0,
        "low": 0.0,
        "status": "error"
    }

@app.route('/')
def home():
    """Ana sayfa rotası."""
    return "Borsa API Backend Sistemi Aktif. Canlı veriler için /api/stocks adresini kullanın."

@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """
    Takip listesindeki tüm hisse senetlerinin canlı verilerini 
    JSON formatında döndüren API uç noktası (Endpoint).
    """
    data_list = []
    for ticker in WATCHLIST:
        stock_info = fetch_stock_data(ticker)
        data_list.append(stock_info)
    return jsonify(data_list)

@app.route('/api/add', methods=['POST'])
def add_to_watchlist():
    """
    Takip listesine yeni bir borsa sembolü ekleme uç noktası.
    Gelen veri JSON formatında 'ticker' parametresi içermelidir.
    """
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Geçersiz parametre. 'ticker' gönderilmelidir."}), 400
        
    new_ticker = data['ticker'].strip().toUpperCase()
    
    if new_ticker not in WATCHLIST:
        WATCHLIST.append(new_ticker)
        return jsonify({"message": f"{new_ticker} başarıyla takip listesine eklendi.", "watchlist": WATCHLIST}), 200
    
    return jsonify({"message": f"{new_ticker} zaten listede mevcut."}), 200

@app.route('/api/delete', methods=['POST'])
def delete_from_watchlist():
    """Takip listesinden sembol silme uç noktası."""
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Geçersiz parametre."}), 400
        
    ticker_to_delete = data['ticker'].strip()
    
    if ticker_to_delete in WATCHLIST:
        WATCHLIST.remove(ticker_to_delete)
        return jsonify({"message": f"{ticker_to_delete} listeden kaldırıldı.", "watchlist": WATCHLIST}), 200
        
    return jsonify({"error": "Sembol listede bulunamadı."}), 404

if __name__ == '__main__':
    # Uygulamayı lokal sunucuda debug modunda başlatıyoruz
    app.run(debug=True, port=5000)
