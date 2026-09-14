<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Tech Solutions | Geleceğe Adım Atın</title>
    <!-- Google Fonts ve FontAwesome (İkonlar için) -->
    <link rel="preconnect" href="https://googleapis.com">
    <link rel="preconnect" href="https://gstatic.com" crossorigin>
    <link href="https://googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cloudflare.com">
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <!-- Navigasyon Menüsü -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="#" class="nav-logo"><i class="fa-solid fa-code"></i> TechCorp</a>
            <ul class="nav-menu">
                <li><a href="#home" class="nav-link">Ana Sayfa</a></li>
                <li><a href="#services" class="nav-link">Hizmetler</a></li>
                <li><a href="#about" class="nav-link">Hakkımızda</a></li>
                <li><a href="#contact" class="nav-link">İletişim</a></li>
            </ul>
            <div class="hamburger">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
        </div>
    </nav>

    <!-- Hero (Giriş) Bölümü -->
    <header id="home" class="hero-section">
        <div class="hero-content">
            <h1>Dijital Dünyada <span class="highlight">Fark Yaratın</span></h1>
            <p>Modern web teknolojileri ve kreatif tasarımlarla işinizi büyütmenize yardımcı oluyoruz.</p>
            <div class="hero-buttons">
                <a href="#services" class="btn btn-primary">Keşfet</a>
                <a href="#contact" class="btn btn-secondary">İletişime Geç</a>
            </div>
        </div>
    </header>

    <!-- Hizmetler Bölümü -->
    <section id="services" class="services-section">
        <div class="section-header">
            <h2>Hizmetlerimiz</h2>
            <p>Sizler için sunduğumuz profesyonel çözümler</p>
        </div>
        <div class="services-grid">
            <div class="service-card">
                <i class="fa-solid fa-laptop-code card-icon"></i>
                <h3>Web Tasarım</h3>
                <p>Kullanıcı dostu, hızlı ve tüm cihazlarla uyumlu (responsive) modern web siteleri üretiyoruz.</p>
            </div>
            <div class="service-card">
                <i class="fa-solid fa-chart-line card-icon"></i>
                <h3>Dijital Pazarlama</h3>
                <p>SEO ve doğru reklam stratejileri ile markanızı arama motorlarında en üst sıralara taşıyoruz.</p>
            </div>
            <div class="service-card">
                <i class="fa-solid fa-shield-halved card-icon"></i>
                <h3>Siber Güvenlik</h3>
                <p>Verilerinizi ve dijital varlıklarınızı en güncel güvenlik protokolleri ile koruma altına alıyoruz.</p>
            </div>
        </div>
    </section>

    <!-- Hakkımızda Bölümü -->
    <section id="about" class="about-section">
        <div class="about-container">
            <div class="about-text">
                <h2>Biz Kimiz?</h2>
                <p>TechCorp olarak, 2020 yılından beri küresel standartlarda yazılım ve tasarım hizmetleri sunan dinamik bir ekibiz. Müşterilerimizin dijital dönüşüm süreçlerini hızlandırıyor ve başarılarına ortak oluyoruz.</p>
                <div class="stats">
                    <div class="stat-item"><h3>150+</h3><p>Proje</p></div>
                    <div class="stat-item"><h3>50+</h3><p>Mutlu Müşteri</p></div>
                </div>
            </div>
            <div class="about-image">
                <img src="https://unsplash.com" alt="Takım Çalışması">
            </div>
        </div>
    </section>

    <!-- İletişim Bölümü -->
    <section id="contact" class="contact-section">
        <div class="section-header">
            <h2>İletişime Geçin</h2>
            <p>Bir projeniz mi var? Bizimle hemen paylaşın.</p>
        </div>
        <div class="contact-container">
            <form id="contact-form" class="contact-form">
                <input type="text" placeholder="Adınız Soyadınız" required>
                <input type="email" placeholder="E-posta Adresiniz" required>
                <textarea placeholder="Mesajınız" rows="5" required></textarea>
                <button type="submit" class="btn btn-primary">Gönder</button>
            </form>
        </div>
    </section>

    <!-- Footer (Alt Bilgi) -->
    <footer class="footer">
        <p>&copy; 2026 TechCorp. Tüm Hakları Saklıdır.</p>
        <div class="social-icons">
            <a href="#"><i class="fa-brands fa-github"></i></a>
            <a href="#"><i class="fa-brands fa-linkedin"></i></a>
            <a href="#"><i class="fa-brands fa-twitter"></i></a>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>
