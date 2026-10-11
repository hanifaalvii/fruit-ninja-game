// Screen Elements
const startupScreen = document.getElementById("startup-screen");
const menuScreen = document.getElementById("menu-screen");
const gameScreen = document.getElementById("game-screen");
const gameoverScreen = document.getElementById("gameover-screen");

const startBtn = document.getElementById("start-btn");
const restartBtn = document.getElementById("restart-btn");
const menuBackBtn = document.getElementById("menu-back-btn");
const modeBtns = document.querySelectorAll(".mode-btn");

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const levelEl = document.getElementById("level");
const livesEl = document.getElementById("lives");
const finalScoreEl = document.getElementById("final-score");
const finalLevelEl = document.getElementById("final-level");

// Game State Variables
let gameMode = "classic"; // classic, arcade, zen
let score = 0;
let level = 1;
let lives = 3;
let gameRunning = false;
let fruits = [];
let sliceTrail = [];

// Audio Beeps / Sound FX (using Web Audio API so it works instantly)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'slice') {
        osc.frequency.setValueAtTime(600, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.1);
    } else if (type === 'bomb') {
        osc.type = 'square';
        osc.frequency.setValueAtTime(150, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.3);
    }
}

// Navigation Events
startBtn.addEventListener("click", () => {
    startupScreen.classList.add("hidden");
    menuScreen.classList.remove("hidden");
});

modeBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
        gameMode = e.currentTarget.getAttribute("data-mode");
        menuScreen.classList.add("hidden");
        gameScreen.classList.remove("hidden");
        startGame();
    });
});

restartBtn.addEventListener("click", () => {
    gameoverScreen.classList.add("hidden");
    gameScreen.classList.remove("hidden");
    startGame();
});

menuBackBtn.addEventListener("click", () => {
    gameoverScreen.classList.add("hidden");
    menuScreen.classList.remove("hidden");
});

function startGame() {
    score = 0;
    level = 1;
    lives = gameMode === 'zen' ? 999 : 3;
    fruits = [];
    gameRunning = true;
    updateHUD();
    gameLoop();
}

function updateHUD() {
    scoreEl.textContent = score;
    levelEl.textContent = level;
    if (gameMode === 'zen') {
        livesEl.textContent = " Zen Mode";
    } else {
        livesEl.textContent = "❤️".repeat(Math.max(0, lives));
    }
}

// Fruit Constructor
class Fruit {
    constructor() {
        this.x = Math.random() * (canvas.width - 200) + 100;
        this.y = canvas.height + 50;
        this.radius = Math.random() * 8 + 25;
        this.dx = (Math.random() - 0.5) * (4 + level);
        this.dy = -(Math.random() * 4 + 11 + (level * 0.5));
        this.gravity = 0.35;
        this.active = true;
        
        // 15% chance to spawn a Bomb in classic/arcade mode
        this.isBomb = (gameMode !== 'zen' && Math.random() < 0.15);
        
        const fruitColors = ["#ff3b30", "#4cd964", "#ffcc00", "#ff9500", "#5ac8fa"];
        this.color = this.isBomb ? "#222" : fruitColors[Math.floor(Math.random() * fruitColors.length)];
        this.label = this.isBomb ? "💣" : "🍉";
    }

    update() {
        this.x += this.dx;
        this.y += this.dy;
        this.dy += this.gravity;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = this.isBomb ? "#ff3b30" : "#ffffff";
        ctx.stroke();
        ctx.closePath();

        ctx.font = "20px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(this.isBomb ? "💣" : "🍎", this.x, this.y);
    }
}

// Track mouse slicing movement
canvas.addEventListener("mousemove", (e) => {
    if (!gameRunning) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    sliceTrail.push({ x: mouseX, y: mouseY, alpha: 1 });
    if (sliceTrail.length > 10) sliceTrail.shift();

    // Check collision with fruits
    fruits.forEach(fruit => {
        if (!fruit.active) return;
        const dist = Math.hypot(mouseX - fruit.x, mouseY - fruit.y);
        if (dist < fruit.radius) {
            fruit.active = false;
            if (fruit.isBomb) {
                playSound('bomb');
                lives -= 2;
                if (lives <= 0) gameOver();
            } else {
                playSound('slice');
                score += 10 * level;
                // Level up every 100 points
                level = Math.floor(score / 100) + 1;
            }
            updateHUD();
        }
    });
});

function gameOver() {
    gameRunning = false;
    gameScreen.classList.add("hidden");
    gameoverScreen.classList.remove("hidden");
    finalScoreEl.textContent = score;
    finalLevelEl.textContent = level;
}

let spawnTimer = 0;
function gameLoop() {
    if (!gameRunning) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Spawn fruit periodically
    spawnTimer++;
    if (spawnTimer > Math.max(20, 70 - (level * 8))) {
        fruits.push(new Fruit());
        if (level >= 3 && Math.random() > 0.5) {
            fruits.push(new Fruit()); // Multi-fruit spawn on higher levels
        }
        spawnTimer = 0;
    }

    // Update and draw fruits
    fruits.forEach((fruit, index) => {
        fruit.update();
        fruit.draw();

        // Check if fruit fell off screen without being sliced
        if (fruit.y > canvas.height + 60 && fruit.active) {
            fruit.active = false;
            if (!fruit.isBomb && gameMode === 'classic') {
                lives--;
                updateHUD();
                if (lives <= 0) gameOver();
            }
        }
    });

    // Cleanup dead fruits
    fruits = fruits.filter(f => f.y < canvas.height + 100);

    // Draw Slicing Trail Blade
    if (sliceTrail.length > 1) {
        ctx.beginPath();
        ctx.moveTo(sliceTrail[0].x, sliceTrail[0].y);
        for (let i = 1; i < sliceTrail.length; i++) {
            ctx.lineTo(sliceTrail[i].x, sliceTrail[i].y);
        }
        ctx.strokeStyle = "rgba(0, 255, 255, 0.7)";
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.closePath();

        // Fade trail
        sliceTrail.forEach(p => p.alpha -= 0.1);
        sliceTrail = sliceTrail.filter(p => p.alpha > 0);
    }

    requestAnimationFrame(gameLoop);
}