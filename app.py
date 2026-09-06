# 🔥 SADECE DEĞİŞTİRİLEN BTA LOGO ALANI (YAVAŞLATILMIŞ BOMBA VE DÖNGÜ EFEKTİ)
bta_bomba_efekti = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 160px; background: transparent; overflow: hidden; margin-top: 15px; margin-bottom: 15px;">
    <canvas id="btaCanvas" width="800" height="150" style="background: transparent;"></canvas>
</div>

<script>
const canvas = document.getElementById('btaCanvas');
const ctx = canvas.getContext('2d');

let bomb = {
    x: canvas.width / 2,
    y: -50,
    targetY: canvas.height / 2 + 10,
    speed: 3, // Düşüş hızı yavaşlatıldı (Eski değer: 8)
    text: "BTA",
    exploded: false
};

let particles = [];
const letters = ["B", "T", "A"];

function createParticles(x, y) {
    for (let i = 0; i < 80; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 3 + 1; // Dağılma hızı yavaşlatıldı (Eski değer: 7+3)
        particles.push({
            x: x,
            y: y,
            char: letters[Math.floor(Math.random() * letters.length)],
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed - Math.random() * 1.5,
            alpha: 1,
            fade: Math.random() * 0.01 + 0.01, // Ekranda kalma süresi uzatıldı
            size: Math.random() * 10 + 18,
            angle: Math.random() * 360,
            rotSpeed: Math.random() * 0.1 - 0.05 // Dönüş hızı yavaşlatıldı
        });
    }
}

function drawLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!bomb.exploded) {
        bomb.y += bomb.speed;
        
        // Düşerken parlayan iz efekti
        for(let i = 0; i < 4; i++) {
            ctx.fillStyle = `rgba(255, 0, 127, ${0.9 - (i * 0.25)})`;
            ctx.font = "bold 65px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(bomb.text, bomb.x, bomb.y - (i * 8));
        }

        if (bomb.y >= bomb.targetY) {
            bomb.exploded = true;
            createParticles(bomb.x, bomb.y);
        }
    } else {
        let activeParticles = 0;
        
        particles.forEach((p) => {
            if (p.alpha > 0) {
                activeParticles++;
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.06; // Yerçekimi ivmesi azaltıldı, daha hafif düşüyorlar
                p.alpha -= p.fade;
                p.angle += p.rotSpeed;

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.angle);
                ctx.fillStyle = `rgba(255, ${Math.floor(Math.random() * 150)}, 255, ${p.alpha})`;
                ctx.font = `bold ${p.size}px Arial`;
                ctx.textAlign = "center";
                ctx.fillText(p.char, 0, 0);
                ctx.restore();
            }
        });

        if (activeParticles === 0) {
            bomb.y = -50;
            bomb.exploded = false;
            particles = [];
        }
    }
    requestAnimationFrame(drawLoop);
}
drawLoop();
</script>
"""
components.html(bta_bomba_efekti, height=160)
