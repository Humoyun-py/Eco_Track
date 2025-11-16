// EcoVerse Welcome Animation
class EcoWelcome {
    constructor() {
        this.userName = 'Foydalanuvchi';
        this.init();
    }

    init() {
        this.createWelcomeScreen();
        this.createNatureElements();
        this.startAnimations();
    }

    createWelcomeScreen() {
        const welcomeHTML = `
            <div class="welcome-container">
                <div class="nature-background" id="natureBg"></div>
                <div class="welcome-content">
                    <div class="welcome-icon">🌍</div>
                    <h1 class="welcome-title">EcoVerse ga Xush Kelibsiz!</h1>
                    <p class="welcome-subtitle">Tabiatni himoya qilish sarguzashti boshlanmoqda</p>
                    <div class="welcome-user" id="userGreeting"></div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('afterbegin', welcomeHTML);
        
        // Foydalanuvchi nomini o'rnatish
        this.setUserName();
    }

    setUserName() {
        // Bu yerda real foydalanuvchi nomini olishingiz mumkin
        const userElement = document.getElementById('userGreeting');
        userElement.textContent = this.userName;
    }

    createNatureElements() {
        const natureBg = document.getElementById('natureBg');
        
        // Barglar yaratish
        for (let i = 0; i < 15; i++) {
            const leaf = document.createElement('div');
            leaf.className = 'leaf-particle';
            leaf.innerHTML = '🍃';
            leaf.style.left = Math.random() * 100 + 'vw';
            leaf.style.animationDuration = (Math.random() * 5 + 3) + 's';
            leaf.style.animationDelay = (Math.random() * 2) + 's';
            natureBg.appendChild(leaf);
        }

        // Suv tomlari yaratish
        for (let i = 0; i < 5; i++) {
            const ripple = document.createElement('div');
            ripple.className = 'water-ripple';
            ripple.style.left = Math.random() * 100 + 'vw';
            ripple.style.top = Math.random() * 100 + 'vh';
            ripple.style.animationDelay = (Math.random() * 3) + 's';
            natureBg.appendChild(ripple);
        }

        // Quyosh nurlari
        const sun = document.createElement('div');
        sun.className = 'sun-rays';
        natureBg.appendChild(sun);

        // Ekologik to'lqin
        const wave = document.createElement('div');
        wave.className = 'eco-wave';
        natureBg.appendChild(wave);
    }

    startAnimations() {
        // 3 soniyadan so'ng welcome ekranini olib tashlash
        setTimeout(() => {
            this.removeWelcomeScreen();
            this.showDashboard();
        }, 3000);
    }

    removeWelcomeScreen() {
        const welcomeContainer = document.querySelector('.welcome-container');
        if (welcomeContainer) {
            welcomeContainer.style.opacity = '0';
            welcomeContainer.style.transform = 'translateY(-50px) scale(0.9)';
            welcomeContainer.style.transition = 'all 0.8s ease-in-out';
            
            setTimeout(() => {
                welcomeContainer.remove();
            }, 800);
        }
    }

    showDashboard() {
        // Dashboard elementlariga animatsiya qo'shish
        const dashboardElements = document.querySelectorAll('.eco-card, .stats-card, .btn-eco-animated');
        dashboardElements.forEach((element, index) => {
            element.style.animationDelay = (index * 0.2) + 's';
        });
    }
}

// DOM yuklanganda ishga tushirish
document.addEventListener('DOMContentLoaded', function() {
    // Faqat login qilgandan keyin ishlaydi
    if (window.location.pathname === '/dashboard' || 
        window.location.pathname === '/dashboard_adult' || 
        window.location.pathname === '/games') {
        new EcoWelcome();
    }
});

// Qo'shimcha utility funksiyalar
function createFloatingAnimation(element) {
    element.classList.add('floating-element');
}

function addEcoHoverEffect(element) {
    element.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px) scale(1.02)';
        this.style.boxShadow = '0 15px 30px rgba(27, 94, 32, 0.3)';
    });
    
    element.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
        this.style.boxShadow = '0 8px 25px rgba(27, 94, 32, 0.1)';
    });
}