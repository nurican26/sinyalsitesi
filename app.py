<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Borsa Tablosu</title>
  <style>
    * {
      box-sizing: border-box;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: #f5f5f5;
      display: flex;
      justify-content: center;
      padding: 20px;
    }

    .widget-container {
      width: 400px;
      background: #fff;
      border: 1px solid #e0e0e0;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Üst Başlık */
    .header-title {
      background-color: #2ed599;
      color: #000;
      text-align: center;
      padding: 12px;
      font-weight: bold;
      font-size: 16px;
    }

    /* Tab/Sekme Butonları */
    .tabs {
      display: flex;
      background-color: #f9f9f9;
      border-bottom: 1px solid #ddd;
    }

    .tab-btn {
      flex: 1;
      padding: 10px 5px;
      text-align: center;
      background: none;
      border: none;
      border-right: 1px solid #ddd;
      font-size: 14px;
      font-weight: bold;
      color: #333;
      cursor: pointer;
    }

    .tab-btn:last-child {
      border-right: none;
    }

    .tab-btn.active {
      background-color: #fff;
      border-top: 3px solid #2ed599;
      color: #000;
    }

    /* Tablo Tasarımı */
    .stock-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    .stock-table th {
      text-align: left;
      padding: 8px;
      background-color: #fff;
      border-bottom: 1px solid #ddd;
      color: #000;
      font-weight: bold;
    }

    .stock-table th:nth-child(2),
    .stock-table th:nth-child(3),
    .stock-table th:nth-child(4) {
      text-align: right;
    }

    .stock-table td {
      padding: 8px;
      border-bottom: 1px dashed #e0e0e0;
    }

    .stock-table tr:nth-child(even) {
      background-color: #fdfdfd;
    }

    .stock-table td:nth-child(2),
    .stock-table td:nth-child(3),
    .stock-table td:nth-child(4) {
      text-align: right;
    }

    /* Değişim Oranı Renkleri */
    .pos-change {
      color: #2ed599;
      font-weight: bold;
    }

    .neg-change {
      color: #e74c3c;
      font-weight: bold;
    }

    .symbol {
      font-weight: bold;
    }
  </style>
</head>
<body>

<div class="widget-container">
  <div class="header-title">Endeks/Dönem Seçimi</div>
  
  <div class="tabs">
    <button class="tab-btn active" onclick="showTab('yukselenler')">Yükselenler</button>
    <button class="tab-btn" onclick="showTab('dusenler')">Düşenler</button>
    <button class="tab-btn" onclick="showTab('hacimliler')">Hacimliler</button>
  </div>

  <table class="stock-table">
    <thead>
      <tr>
        <th>HİSSE</th>
        <th>SON</th>
        <th>DEĞİŞİM</th>
        <th>HACİM (mTL)</th>
      </tr>
    </thead>
    <tbody id="table-body">
      <!-- Veriler JavaScript ile buraya eklenecek -->
    </tbody>
  </table>
</div>

<script>
  // Örnek Borsa Verileri
  const data = {
    yukselenler: [
      { symbol: 'PATEK', price: '25.16', change: '9.97 %', volume: '1,904.22' },
      { symbol: 'TKFEN', price: '230.00', change: '6.33 %', volume: '2,595.34' },
      { symbol: 'ZOREN', price: '2.52', change: '4.56 %', volume: '825.48' },
      { symbol: 'DSTKF', price: '2,720.00', change: '4.41 %', volume: '1,458.11' },
      { symbol: 'ENERY', price: '12.70', change: '2.42 %', volume: '763.78' },
      { symbol: 'REEDR', price: '5.35', change: '1.33 %', volume: '577.29' },
      { symbol: 'ASELS', price: '377.00', change: '1.21 %', volume: '9,858.86' },
      { symbol: 'ANSGR', price: '26.78', change: '0.68 %', volume: '148.66' }
    ],
    dusenler: [
      { symbol: 'THYAO', price: '280.50', change: '-3.20 %', volume: '4,120.00' },
      { symbol: 'GARAN', price: '112.00', change: '-2.15 %', volume: '3,850.50' }
    ],
    hacimliler: [
      { symbol: 'ASELS', price: '377.00', change: '1.21 %', volume: '9,858.86' },
      { symbol: 'THYAO', price: '280.50', change: '-3.20 %', volume: '4,120.00' }
    ]
  };

  function showTab(type) {
    // Sekme aktifliğini değiştir
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Tablo içeriğini doldur
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    data[type].forEach(item => {
      const isNegative = item.change.includes('-');
      const changeClass = isNegative ? 'neg-change' : 'pos-change';

      const row = `
        <tr>
          <td class="symbol">${item.symbol}</td>
          <td>${item.price}</td>
          <td class="${changeClass}">${item.change}</td>
          <td>${item.volume}</td>
        </tr>
      `;
      tbody.innerHTML += row;
    });
  }

  // Başlangıçta Yükselenler sekmesini yükle
  showTab('yukselenler');
</script>

</body>
</html>
