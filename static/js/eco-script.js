// EcoVerse JavaScript fayli

// Umumiy funksiyalar
document.addEventListener('DOMContentLoaded', function() {
    initEcoVerse();
});

function initEcoVerse() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Notification system
    window.showEcoNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} eco-notification`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Animatsiya
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };

    // Energy and coins animation
    window.animateValue = function(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };
}

// API funksiyalari
const EcoAPI = {
    // Topshiriq bajarish
    completeTask: async function(taskId) {
        try {
            const response = await fetch(`/complete_task/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Topshiriq bajarishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Item sotib olish
    buyItem: async function(itemId) {
        try {
            const response = await fetch(`/buy_item/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Item sotib olishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Item kiyish
    equipItem: async function(itemId) {
        try {
            const response = await fetch(`/equip_item/${itemId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Item kiyishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Post yaratish
    createPost: async function(formData) {
        try {
            const response = await fetch('/create_post', {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Post yaratishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Izoh qo'shish
    addComment: async function(postId, text) {
        try {
            const response = await fetch(`/add_comment/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            return await response.json();
        } catch (error) {
            console.error('Izoh qo\'shishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Xabar yuborish
    sendMessage: async function(receiverId, text) {
        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ receiver_id: receiverId, text: text })
            });
            return await response.json();
        } catch (error) {
            console.error('Xabar yuborishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    },

    // Xabarlarni olish
    getMessages: async function(userId) {
        try {
            const response = await fetch(`/get_messages/${userId}`);
            return await response.json();
        } catch (error) {
            console.error('Xabarlarni olishda xatolik:', error);
            return { success: false, error: 'Tarmoq xatosi' };
        }
    }
};

// Event handler'lar
document.addEventListener('click', function(e) {
    // Topshiriq bajarish
    if (e.target.classList.contains('complete-task')) {
        e.preventDefault();
        const taskId = e.target.dataset.taskId;
        handleCompleteTask(taskId, e.target);
    }

    // Item sotib olish
    if (e.target.classList.contains('buy-item')) {
        e.preventDefault();
        const itemId = e.target.dataset.itemId;
        handleBuyItem(itemId, e.target);
    }

    // Item kiyish
    if (e.target.classList.contains('equip-item')) {
        e.preventDefault();
        const itemId = e.target.dataset.itemId;
        handleEquipItem(itemId, e.target);
    }
});

// Handler funksiyalari
async function handleCompleteTask(taskId, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    const result = await EcoAPI.completeTask(taskId);
    
    if (result.success) {
        showEcoNotification(result.message, 'success');
        // Qiymatlarni yangilash
        updateUserStats(result);
        setTimeout(() => location.reload(), 1000);
    } else {
        showEcoNotification(result.error, 'danger');
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

async function handleBuyItem(itemId, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    const result = await EcoAPI.buyItem(itemId);
    
    if (result.success) {
        showEcoNotification(result.message, 'success');
        updateUserStats(result);
        setTimeout(() => location.reload(), 1000);
    } else {
        showEcoNotification(result.error, 'danger');
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

async function handleEquipItem(itemId, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    const result = await EcoAPI.equipItem(itemId);
    
    if (result.success) {
        showEcoNotification(result.message, 'success');
        setTimeout(() => location.reload(), 1000);
    } else {
        showEcoNotification(result.error, 'danger');
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// User statistikasini yangilash
function updateUserStats(data) {
    const coinElements = document.querySelectorAll('.user-coins');
    const energyElements = document.querySelectorAll('.user-energy');
    
    coinElements.forEach(el => {
        if (data.coins !== undefined) {
            const currentCoins = parseInt(el.textContent) || 0;
            animateValue(el, currentCoins, data.coins, 1000);
        }
    });
    
    energyElements.forEach(el => {
        if (data.energy !== undefined) {
            el.textContent = data.energy;
        }
    });
}

// Xabarlashuv tizimi
class EcoChat {
    constructor() {
        this.currentChat = null;
        this.messages = [];
    }

    loadConversation(userId) {
        this.currentChat = userId;
        EcoAPI.getMessages(userId).then(result => {
            if (result.success) {
                this.displayMessages(result.messages);
            }
        });
    }

    displayMessages(messages) {
        const container = document.getElementById('chatMessages');
        container.innerHTML = '';
        
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message-bubble ${msg.is_sent ? 'message-sent' : 'message-received'}`;
            messageDiv.innerHTML = `
                <div class="message-text">${msg.text}</div>
                <div class="message-time">${msg.timestamp}</div>
            `;
            container.appendChild(messageDiv);
        });
        
        container.scrollTop = container.scrollHeight;
    }

    sendMessage(text) {
        if (!this.currentChat || !text.trim()) return;
        
        EcoAPI.sendMessage(this.currentChat, text).then(result => {
            if (result.success) {
                this.loadConversation(this.currentChat);
            }
        });
    }
}

// Global chat instance
window.ecoChat = new EcoChat();