# 🟢 SADECE DEĞİŞTİRİLEN BTA LOGO ALANI (ZİKZAKLI DOLANAN NEON YEŞİL EFEKT)
bta_bomba_efekti = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 160px; background: transparent; overflow: hidden; margin-top: 15px; margin-bottom: 15px;">
    <canvas id="btaCanvas" width="800" height="150" style="background: transparent;"></canvas>
</div>

<script>
const canvas = document.getElementById('btaCanvas');
const ctx = canvas.getContext('2d');

let textObj = {
    x: canvas.width / 2,
    y: -30,
    targetY: canvas.height / 2 + 10,
    speedY: 2.5,
    angle: 0,
    amp: 45, // Zikzak genişliği
    text: "BTA",
    fadedOut: false
};

let particles = [];
const letters = ["B", "T", "A"];

function createParticles(x, y) {
    for (let i = 0; i < 60; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 2 + 0.5; // Yumuşak dağılma hızı
        particles.push({
            x: x,
            y: y,
            char: letters[Math.floor(Math.random() * letters.length)],
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            alpha: 1,
            fade: Math.random() * 0.015 + 0.01,
            size: Math.random() * 8 + 18,
            angle: Math.random() * 360,
            rotSpeed: Math.random() * 0.05 - 0.025
        });
    }
}

function drawLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!textObj.fadedOut) {
        // Aşağı inerken zikzak çizme mekanizması
        textObj.y += textObj.speedY;
        textObj.angle += 0.07; 
        let currentX = (canvas.width / 2) + Math.sin(textObj.angle) * textObj.amp;

        // Dolanırken arkasında bıraktığı süzülen neon yeşil izler
        for(let i = 0; i < 5; i++) {
            let trailAlpha = 0.9 - (i * 0.18);
            ctx.fillStyle = `rgba(0, 255, 127, ${trailAlpha})`; // Neon Yeşil / Turkuaz tonu
            ctx.font = "bold 65px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            
            // İzlerin geçmiş x koordinatını hesapla
            let trailX = (canvas.width / 2) + Math.sin(textObj.angle - (i * 0.2)) * textObj.amp;
            ctx.fillText(textObj.text, trailX, textObj.y - (i * 6));
        }

        if (textObj.y >= textObj.targetY) {
            textObj.fadedOut = true;
            createParticles(currentX, textObj.y);
        }
    } else {
        let activeParticles = 0;
        
        particles.forEach((p) => {
            if (p.alpha > 0) {
                activeParticles++;
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.02; // Çok hafif süzülme etkisi (Bomba düşüşü kaldırıldı)
                p.alpha -= p.fade;
                p.angle += p.rotSpeed;

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.angle);
                // Matris yeşili tonlarında dağılan harfler
                ctx.fillStyle = `rgba(50, 255, ${Math.floor(Math.random() * 100 + 100)}, ${p.alpha})`;
                ctx.font = `bold ${p.size}px Arial`;
                ctx.textAlign = "center";
                ctx.fillText(p.char, 0, 0);
                ctx.restore();
            }
        });

        if (activeParticles === 0) {
            textObj.y = -30;
            textObj.angle = 0;
            textObj.fadedOut = false;
            particles = [];
        }
    }
    requestAnimationFrame(drawLoop);
}
drawLoop();
</script>
"""
components.html(bta_bomba_efekti, height=160)
