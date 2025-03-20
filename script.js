const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
let particles = [];
let mouse = { x: null, y: null, radius: 150 };

class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = Math.random() * 2 - 1;
        this.vy = Math.random() * 2 - 1;
        this.radius = 2;
    }
    move() {
        let dx = this.x - mouse.x;
        let dy = this.y - mouse.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < mouse.radius) {
            this.x -= dx * 0.05;
            this.y -= dy * 0.05;
        }
        
        this.x += this.vx;
        this.y += this.vy;
        if (this.x > canvas.width || this.x < 0) this.vx *= -1;
        if (this.y > canvas.height || this.y < 0) this.vy *= -1;
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = "white";
        ctx.fill();
    }
}

function createParticles() {
    for (let i = 0; i < 100; i++) {
        particles.push(new Particle(Math.random() * canvas.width, Math.random() * canvas.height));
    }
}

function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            let dx = particles[i].x - particles[j].x;
            let dy = particles[i].y - particles[j].y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100) {
                ctx.strokeStyle = `rgba(255, 255, 255, ${1 - distance / 100})`;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => p.move());
    connectParticles();
    particles.forEach(p => p.draw());
    requestAnimationFrame(animate);
}

window.addEventListener("mousemove", event => {
    mouse.x = event.x;
    mouse.y = event.y;
});

function checkFraud(event) {
    event.preventDefault(); // Prevent page refresh

    const inputData = document.getElementById("inputData").value.trim(); // Get input value
    const resultsSection = document.getElementById("results-section");
    const resultMessage = document.querySelector(".result-message");

    if (!inputData) {
        resultMessage.textContent = "❌ Please enter a valid phone number or website!";
        resultsSection.hidden = false;
        return;
    }

    fetch("http://127.0.0.1:5000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: inputData })  // Use inputData instead of phoneNumber
    })
    .then(response => response.json())
    .then(data => {
        console.log("Received from server:", data); // Debugging
        let output = "";
        
        if (data.status) {
            output = data.message || "Unknown status";
        } else {
            output = `🌍 Domain Age: ${data.domain_age}\n🔎 Analysis: ${data.content_analysis}`;
        }

        resultMessage.textContent = output;
        resultsSection.hidden = false;
    })
    .catch(error => {
        console.error("Fetch error:", error);
        resultMessage.textContent = "❌ Error connecting to the server!";
        resultsSection.hidden = false;
    });
}

createParticles();
animate();
