const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const scoreElement = document.getElementById("score");

let score = 0;

// Fruit object
let fruit = {
    x: 400,
    y: 540,
    radius: 30,
    color: "#ff3b30", // Red fruit
    dx: 2,
    dy: -14,
    gravity: 0.35,
    active: true
};

function resetFruit() {
    fruit.x = Math.random() * 600 + 100;
    fruit.y = canvas.height + 40;
    fruit.dx = (Math.random() - 0.5) * 6;
    fruit.dy = -(Math.random() * 4 + 11);
    
    // Randomize colors for different fruits!
    const colors = ["#ff3b30", "#4cd964", "#ffcc00", "#ff9500"];
    fruit.color = colors[Math.floor(Math.random() * colors.length)];
    fruit.active = true;
}

// Track mouse slicing
canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Check if mouse collides with fruit
    const distance = Math.hypot(mouseX - fruit.x, mouseY - fruit.y);
    if (distance < fruit.radius && fruit.active) {
        fruit.active = false;
        score += 10;
        scoreElement.textContent = score;
        setTimeout(resetFruit, 600); // Launch next fruit shortly
    }
});

function update() {
    if (fruit.active) {
        fruit.x += fruit.dx;
        fruit.y += fruit.dy;
        fruit.dy += fruit.gravity; // Gravity pulls it back down

        // If it falls off the bottom screen
        if (fruit.y > canvas.height + 60) {
            resetFruit();
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (fruit.active) {
        // Draw Fruit
        ctx.beginPath();
        ctx.arc(fruit.x, fruit.y, fruit.radius, 0, Math.PI * 2);
        ctx.fillStyle = fruit.color;
        ctx.fill();
        ctx.closePath();

        // Draw Stem/Leaf
        ctx.fillStyle = "#2ecc71";
        ctx.fillRect(fruit.x - 3, fruit.y - fruit.radius - 6, 6, 8);
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Start game
gameLoop();