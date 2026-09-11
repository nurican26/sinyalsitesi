<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yıldız Panel - Beğeni Paneli</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #0b111e;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .panel-container {
            width: 100%;
            max-width: 800px;
            background: linear-gradient(145deg, #0f172a, #131c33);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }

        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #00f2fe;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.6);
            letter-spacing: 2px;
        }

        .status {
            font-size: 13px;
            color: #00ff87;
            background: rgba(0, 255, 135, 0.1);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 135, 0.3);
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        input, select {
            width: 100%;
            padding: 14px;
            background-color: #090d16;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #ffffff;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #00f2fe;
            box-shadow: 0 0 8px rgba(0, 242, 254, 0.4);
        }

        .info-box {
            background-color: rgba(255, 234, 0, 0.05);
            border: 1px solid rgba(255, 234, 0, 0.2);
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            color: #e2e8f0;
            margin-bottom: 25px;
            line-height: 1.5;
        }

        .info-box span {
            color: #ffea00;
            font-weight: bold;
        }

        .submit-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(90deg, #00f2fe, #4facfe);
            border: none;
            border-radius: 8px;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
        }

        .submit-btn:active {
            transform: translateY(1px);
        }
    </style>
</head>
<body>

    <div class="panel-container">
        <div class="panel-header">
            <div class="logo">YILDIZ PANEL</div>
            <div class="status">● Sistem Aktif</div>
        </div>

        <form onsubmit="event.preventDefault(); alert('Beğeni işlemi başlatıldı!');">
            <div class="form-group">
                <label for="platform">Platform Seçimi</label>
                <select id="platform">
                    <option value="instagram">Instagram Beğeni</option>
                    <option value="tiktok">TikTok Beğeni</option>
                    <option value="twitter">X (Twitter) Beğeni</option>
                    <option value="youtube">YouTube Beğeni</option>
                </select>
            </div>

            <div class="form-group">
                <label for="url">Gönderi Bağlantısı (URL)</label>
                <input type="url" id="url" placeholder="https://..." required>
            </div>

            <div class="form-group">
                <label for="quantity">Beğeni Miktarı</label>
                <input type="number" id="quantity" placeholder="Örn: 500" min="10" max="10000" required>
            </div>

            <div class="info-box">
                <span>⚠️ YASAL UYARI & BİLGİLENDİRME:</span> Gönderim süresi yoğunluğa bağlı olarak 15 dakikaya kadar gecikebilir. Hesap gizliliğinizin "Kamuya Açık" (Herkese Açık) olduğundan emin olunuz. Gizli hesaplara gönderim yapılamamaktadır.
            </div>

            <button type="submit" class="submit-btn">Beğeni Gönderimini Başlat</button>
        </form>
    </div>

</body>
</html>
