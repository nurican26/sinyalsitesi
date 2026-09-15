<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>BİST Canlı Piyasa Hareketleri</title>
  <style>
    body {
      background-color: #0b111e;
      font-family: Arial, sans-serif;
      color: #ffffff;
      padding: 20px;
    }

    /* Ana Kart Konfigürasyonu */
    .widget-card {
      width: 450px;
      background-color: #050c17;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid #1a2638;
      box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    /* Başlık Alanı */
    .widget-header {
      background-color: #00f2c3;
      color: #000000;
      text-align: center;
      padding: 12px;
      font-weight: bold;
      font-size: 16px;
    }

    /* Sekme Alanı */
    .tabs {
      display: flex;
      background-color: #091424;
      border-bottom: 1px solid #1a2638;
    }
    .tab {
      flex: 1;
      padding: 10px;
      text-align: center;
      font-size: 13px;
      font-weight: bold;
      cursor: pointer;
    }
    .tab.active {
      background-color: #0e1d33;
      color: #00f2c3;
      border-bottom: 2px solid #00f2c3;
    }

    /* Tablo Tasarımı */
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }
    th {
      color: #00f2c3;
      font-size: 11px;
      padding: 10px 12px;
      border-bottom: 1px solid #1a2638;
      text-transform: uppercase;
    }
    td {
      padding: 10px 12px;
      font-size: 13px;
      border-bottom: 1px dashed #142033;
    }
    tr:hover {
      background-color: #0e1d33;
    }

    /* Özel Sütun Hizalamaları ve Renkler */
    .text-right { text-align: right; }
    .val-green { color: #00f2c3; font-weight: bold; }
    .col-hacim { color: #8a9ba8; }
  </style>
</head>
<body>

<div class="widget-card">
  <!-- Güncellenen Başlık -->
  <div class="widget-header">
    BİST Hacimli Yükselenler
  </div>

  <div class="tabs">
    <div class="tab active">📈 Yükselenler / Tavanlar</div>
    <div class="tab">📉 En Çok Düşenler</div>
  </div>

  <!-- Hacim Sütunlu Tablo -->
  <table>
    <thead>
      <tr>
        <th>HİSSE</th>
        <th class="text-right">SON (TL)</th>
        <th class="text-right col-hacim">HACİM (TL)</th>
        <th class="text-right">DEĞİŞİM</th>
      </tr>
    </thead>
    <tbody id="bist-data">
      <!-- Veriler JavaScript ile dinamik beslenir -->
    </tbody>
  </table>
</div>

<script>
  // Örnek BİST Veri Seti (Hacim bilgisi eklendi)
  const hisseVerileri = [
    { kod: "RTALB", son: 3.03, hacim: "145.2M", degisim: 10.58 },
    { kod: "IHYAY", son: 1.36, hacim: "98.4M", degisim: 9.68 },
    { kod: "TDGYO", son: 18.62, hacim: "210.5M", degisim: 9.40 },
    { kod: "KARSN", son: 14.33, hacim: "540.1M", degisim: 7.10 },
    { kod: "EGEEN", son: 6522.50, hacim: "890.3M", degisim: 5.84 },
    { kod: "AKSUE", son: 28.76, hacim: "67.8M", degisim: 5.81 },
    { kod: "IHLGM", son: 1.73, hacim: "112.0M", degisim: 5.49 },
    { kod: "ALCAR", son: 754.00, hacim: "345.6M", degisim: 5.45 },
    { kod: "EDATA", son: 17.27, hacim: "88.9M", degisim: 5.30 }
  ];

  const tbody = document.getElementById("bist-data");

  hisseVerileri.forEach(hisse => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${hisse.kod}</strong></td>
      <td class="text-right">${hisse.son.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
      <td class="text-right col-hacim">${hisse.hacim}</td>
      <td class="text-right val-green">+${hisse.degisim.toFixed(2)} %</td>
    `;
    tbody.appendChild(row);
  });
</script>

</body>
</html>
