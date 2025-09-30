// 📱 HimigTube PWA (Progressive Web App) Functionality
// Install prompt and service worker registration

let deferredPrompt;
let installButton;

// Check if PWA is already installed
function isPWAInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches || 
           window.navigator.standalone === true;
}

// Check if device is mobile
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           window.innerWidth <= 768;
}

// Add permanent install button to header (mobile only)
function addInstallButton() {
    if (isPWAInstalled() || !isMobileDevice()) return;
    
    const header = document.querySelector('.header');
    if (!header || document.getElementById('pwa-install-header-btn')) return;
    
    const installBtn = document.createElement('button');
    installBtn.id = 'pwa-install-header-btn';
    installBtn.className = 'pwa-header-install-btn';
    installBtn.innerHTML = '📲 Install App';
    installBtn.title = 'Install HimigTube as an app';
    
    installBtn.addEventListener('click', () => {
        // Only trigger native browser prompt
        if (deferredPrompt) {
            installPWA();
        }
        // If no prompt available, browser will show install option in menu/address bar automatically
    });
    
    header.appendChild(installBtn);
}

// Show install banner (mobile only)
function showInstallBanner() {
    if (isPWAInstalled() || !isMobileDevice()) return;
    
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.className = 'pwa-banner animate-slide-down';
    banner.innerHTML = `
        <div class="pwa-banner-content">
            <div class="pwa-icon">📱</div>
            <div class="pwa-text">
                <h4>Install HimigTube App</h4>
                <p>Get faster access! Install HimigTube as an app on your device.</p>
            </div>
            <div class="pwa-buttons">
                <button id="pwa-install-btn" class="pwa-install-btn">📲 Install</button>
                <button id="pwa-close-btn" class="pwa-close-btn">✕</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(banner);
    
    // Add event listeners
    document.getElementById('pwa-install-btn').addEventListener('click', installPWA);
    document.getElementById('pwa-close-btn').addEventListener('click', () => {
        banner.remove();
        localStorage.setItem('pwa-banner-dismissed', Date.now());
    });
}

async function installPWA() {
    if (!deferredPrompt) {
        // No native prompt available - browser will show it when criteria are met
        return;
    }
    
    // Show the install prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
        console.log('🎉 HimigTube PWA installed successfully!');
        // Remove banner and button
        const banner = document.getElementById('pwa-install-banner');
        const headerBtn = document.getElementById('pwa-install-header-btn');
        if (banner) banner.remove();
        if (headerBtn) headerBtn.remove();
    }
    
    // Clear the deferredPrompt
    deferredPrompt = null;
}

// Listen for beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    
    // Save the event so it can be triggered later
    deferredPrompt = e;
    
    // Check if this is a first-time user
    const isFirstTime = !localStorage.getItem('pwa-banner-dismissed') && !localStorage.getItem('pwa-first-visit');
    
    // Check if banner was recently dismissed
    const dismissed = localStorage.getItem('pwa-banner-dismissed');
    const daysSinceDismissed = dismissed ? (Date.now() - parseInt(dismissed)) / (1000 * 60 * 60 * 24) : 999;
    
    if (isFirstTime) {
        // For first-time users, show immediately with a more prominent prompt
        localStorage.setItem('pwa-first-visit', Date.now());
        setTimeout(showFirstTimeInstallPrompt, 1000); // Show after 1 second for first-timers
    } else if (daysSinceDismissed > 3) {
        // For returning users, show banner if not dismissed recently (wait 3 days)
        setTimeout(showInstallBanner, 3000); // Show after 3 seconds
    }
});

// Show prominent install prompt for first-time users (mobile only)
function showFirstTimeInstallPrompt() {
    if (isPWAInstalled() || !isMobileDevice()) return;
    
    const prompt = document.createElement('div');
    prompt.id = 'pwa-first-time-prompt';
    prompt.className = 'pwa-first-time-modal animate-fade-in';
    prompt.innerHTML = `
        <div class="pwa-first-time-content">
            <div class="pwa-first-time-header">
                <div class="pwa-welcome-icon">🎉</div>
                <h2>Welcome to HimigTube!</h2>
                <p>Install our app for the best experience</p>
            </div>
            <div class="pwa-benefits">
                <div class="benefit-item">
                    <span class="benefit-icon">⚡</span>
                    <span>Faster loading</span>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">📱</span>
                    <span>Works offline</span>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">🏠</span>
                    <span>Home screen access</span>
                </div>
            </div>
            <div class="pwa-first-time-buttons">
                <button id="pwa-first-install-btn" class="pwa-primary-btn">
                    📲 Install HimigTube
                </button>
                <button id="pwa-first-later-btn" class="pwa-secondary-btn">
                    Maybe Later
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(prompt);
    
    // Add event listeners
    document.getElementById('pwa-first-install-btn').addEventListener('click', () => {
        installPWA();
        prompt.remove();
    });
    
    document.getElementById('pwa-first-later-btn').addEventListener('click', () => {
        prompt.remove();
        localStorage.setItem('pwa-banner-dismissed', Date.now());
    });
    
    // Close on backdrop click
    prompt.addEventListener('click', (e) => {
        if (e.target === prompt) {
            prompt.remove();
            localStorage.setItem('pwa-banner-dismissed', Date.now());
        }
    });
}

// Listen for app installed event
window.addEventListener('appinstalled', () => {
    console.log('🎉 HimigTube PWA was installed successfully!');
    
    // Remove banner and button if still visible
    const banner = document.getElementById('pwa-install-banner');
    const headerBtn = document.getElementById('pwa-install-header-btn');
    if (banner) banner.remove();
    if (headerBtn) headerBtn.remove();
    
    // Clear dismissed flag
    localStorage.removeItem('pwa-banner-dismissed');
    
    // Show success message
    showInstallSuccessMessage();
});

// Show success message after installation
function showInstallSuccessMessage() {
    const message = document.createElement('div');
    message.className = 'pwa-success-message animate-fade-in';
    message.innerHTML = `
        <div class="success-content">
            <div class="success-icon">🎉</div>
            <h4>HimigTube Installed!</h4>
            <p>You can now access HimigTube from your home screen!</p>
        </div>
    `;
    
    document.body.appendChild(message);
    
    // Remove after 5 seconds
    setTimeout(() => {
        message.classList.add('animate-fade-out');
        setTimeout(() => message.remove(), 300);
    }, 5000);
}

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
        try {
            const registration = await navigator.serviceWorker.register('/static/converter/js/sw.js');
            console.log('🔧 Service Worker registered successfully:', registration.scope);
        } catch (error) {
            console.log('❌ Service Worker registration failed:', error);
        }
    });
}

// Initialize PWA functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add permanent install button to header (mobile only)
    setTimeout(addInstallButton, 1000);
    
    // Add PWA styles if not already added
    if (!document.getElementById('pwa-styles')) {
        const style = document.createElement('style');
        style.id = 'pwa-styles';
        style.textContent = `
            .pwa-header-install-btn {
                background: linear-gradient(135deg, #ff6b9d, #c44569);
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(255, 107, 157, 0.3), 0 0 20px rgba(255, 255, 255, 0.4);
                margin-left: auto;
                animation: glow-pulse 2s ease-in-out infinite alternate;
            }
            
            .pwa-header-install-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4), 0 0 30px rgba(255, 255, 255, 0.6);
                background: linear-gradient(135deg, #ff5588, #b83d5a);
            }
            
            @keyframes glow-pulse {
                from {
                    box-shadow: 0 2px 10px rgba(255, 107, 157, 0.3), 0 0 20px rgba(255, 255, 255, 0.4);
                }
                to {
                    box-shadow: 0 2px 10px rgba(255, 107, 157, 0.3), 0 0 30px rgba(255, 255, 255, 0.8);
                }
            }
                
            .pwa-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #ff6b9d, #c44569);
                color: white;
                z-index: 10000;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                animation: slideDown 0.5s ease-out;
            }
            
            .pwa-banner-content {
                display: flex;
                align-items: center;
                padding: 1rem;
                max-width: 1200px;
                margin: 0 auto;
                gap: 1rem;
            }
            
            .pwa-icon {
                font-size: 2rem;
                flex-shrink: 0;
            }
            
            .pwa-text {
                flex: 1;
            }
            
            .pwa-text h4 {
                margin: 0 0 0.25rem 0;
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .pwa-text p {
                margin: 0;
                font-size: 0.9rem;
                opacity: 0.9;
            }
            
            .pwa-buttons {
                display: flex;
                gap: 0.5rem;
                flex-shrink: 0;
            }
            
            .pwa-install-btn {
                background: rgba(255,255,255,0.2);
                border: 2px solid rgba(255,255,255,0.5);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pwa-install-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }
            
            .pwa-close-btn {
                background: transparent;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 50%;
                width: 35px;
                height: 35px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }
            
            .pwa-close-btn:hover {
                background: rgba(255,255,255,0.2);
            }
            
            .pwa-success-message {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                z-index: 10001;
                text-align: center;
                max-width: 300px;
            }
            
            .success-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .success-content h4 {
                color: #ff6b9d;
                margin: 0 0 0.5rem 0;
            }
            
            .success-content p {
                color: #666;
                margin: 0;
            }
            
            .pwa-first-time-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                z-index: 10002;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }
            
            .pwa-first-time-content {
                background: white;
                border-radius: 20px;
                padding: 2rem;
                max-width: 500px;
                width: 100%;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            .pwa-first-time-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .pwa-welcome-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .pwa-first-time-header h2 {
                color: #ff6b9d;
                margin: 0 0 0.5rem 0;
            }
            
            .pwa-first-time-header p {
                color: #666;
                margin: 0;
            }
            
            .pwa-benefits {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .benefit-item {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #ff6b9d;
                flex: 1;
            }
            
            .benefit-icon {
                font-size: 1.5rem;
                margin-right: 0.5rem;
            }
            
            .pwa-first-time-buttons {
                display: flex;
                gap: 0.5rem;
                flex-shrink: 0;
            }
            
            .pwa-primary-btn {
                background: linear-gradient(135deg, #ff6b9d, #c44569);
                color: white;
                border: none;
                padding: 0.75rem 2rem;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pwa-primary-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4);
            }
            
            .pwa-secondary-btn {
                background: transparent;
                border: 2px solid #ff6b9d;
                color: #ff6b9d;
                padding: 0.75rem 2rem;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pwa-secondary-btn:hover {
                background: rgba(255, 107, 157, 0.2);
            }
            
            @keyframes slideDown {
                from { transform: translateY(-100%); }
                to { transform: translateY(0); }
            }
            
            @media (max-width: 768px) {
                .pwa-banner-content {
                    flex-direction: column;
                    text-align: center;
                    gap: 0.75rem;
                }
                
                .pwa-text h4 {
                    font-size: 1rem;
                }
                
                .pwa-text p {
                    font-size: 0.85rem;
                }
                
                .pwa-header-install-btn {
                    font-size: 0.8rem;
                    padding: 0.4rem 0.8rem;
                }
            }
        `;
        document.head.appendChild(style);
    }
});
