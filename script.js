// Mobil Menü (Hamburger) Tetikleyicisi
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    navMenu.classList.toggle("active");
});

// Menü linklerine tıklandığında menüyü otomatik kapat
document.querySelectorAll(".nav-link").forEach(n => n.addEventListener("click", () => {
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
}));

// İletişim Formu Kontrolü
const contactForm = document.getElementById("contact-form");

if(contactForm) {
    contactForm.addEventListener("submit", function(e) {
        e.preventDefault(); // Sayfa yenilenmesini engeller
        
        // Form verilerini simüle edilmiş başarılı bir alert ile taçlandırıyoruz
        alert("Mesajınız başarıyla alındı! En kısa sürede dönüş yapacağız.");
        contactForm.reset(); // Formu temizler
    });
}
