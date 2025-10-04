# 🎶 HimigTube - Pinoy YouTube to MP3 Converter 🇵🇭

**HimigTube** is a Filipino-themed YouTube to MP3 downloader built using Django + yt-dlp + FFmpeg, designed especially for music lovers who want to convert YouTube songs directly into downloadable MP3 files — all wrapped in a vibrant, Pinoy-inspired experience with hugot feels, loading animations, and progressive processing UI.

> 📅 Released: August 13, 2025  
> 💻 Built by: A Computer Science student from the Philippines  
> 🛠 Hosted on: Render + GitHub  
> 🌍 Website: [https://himigtube.render.com](#)

---

## 🚀 Features

- 🎧 **Smart Search** - Search any YouTube music using title, artist, or lyrics
- 🔄 **High-Quality Conversion** - Converts YouTube audio to MP3 with customizable bitrate options
- 💬 **Hugot Loading** - Displays funny hugot-style comments during processing
- 🌀 **Animated Progress** - Progress bar with animation and meme GIFs to entertain users
- 📥 **Auto Download** - Automatic download after conversion
- 📱 **PWA Support** - Install as mobile app on Android/iOS devices
- 🎨 **Filipino-Inspired Design** - Colors, fonts, and banners with Pinoy pride
- ✨ **Enhanced Mobile Experience** - Unique glowing effects and animations for mobile users
- 🧭 **Interactive Navigation** - Smooth tab switching with hover effects

---

<<<<<<< HEAD
## 🆕 Latest Updates (v2.0)
=======
## 🆕 Latest Updates (v1.2)
>>>>>>> 9fa374110cd555a6c03f63fcb132411716adcb2e

### 📱 **Progressive Web App (PWA) Enhancement**
- **Mobile App Installation** - Users can now install HimigTube as a native-like app on their phones
- **Offline Capability** - Works offline with cached resources
- **Native Browser Integration** - Uses browser's built-in install prompts for seamless experience
- **Home Screen Icon** - Appears as a real app icon on mobile home screens

### 🎨 **UI/UX Improvements**
- **Interactive Navigation Tabs** - Added hover and active states with pink gradient effects
- **Fixed Search Results Display** - Resolved issue where search results weren't showing properly
- **Enhanced Card Layouts** - Beautiful card-based design for search results with hover animations
- **Mobile-First Design** - Unique glowing effects and stronger visual feedback for mobile users

### 🔧 **Technical Enhancements**
- **Responsive Design** - Improved mobile responsiveness across all screen sizes
- **Performance Optimization** - Faster loading and smoother animations
- **Code Cleanup** - Removed redundant code and improved maintainability

---

## 📱 PWA Installation Guide

### **Android (Chrome/Edge)**
1. Open HimigTube in Chrome or Edge browser
2. Look for the "📲 Install App" button in the header
3. Tap "Install" when browser prompt appears
4. App will be added to your home screen

### **iOS (Safari)**
1. Open HimigTube in Safari
2. Tap the Share button (square with arrow)
3. Select "Add to Home Screen"
4. Confirm installation

### **Desktop**
1. Visit HimigTube in Chrome, Edge, or Firefox
2. Look for install icon in address bar
3. Click "Install HimigTube" when prompted

---

## 🛠 Built With

- **Backend:** Python 3.11+, Django 4.x
- **Audio Processing:** yt-dlp, FFmpeg
- **Frontend:** HTML5, CSS3, JavaScript
- **PWA:** Service Worker, Web Manifest
- **APIs:** YouTube Search Python, RapidAPI
- **Styling:** Custom CSS with Filipino-inspired design
- **Deployment:** Render.com
- **Version Control:** GitHub

---

## 📂 Project Structure
himigtube/ ├── himigtube/ # Django project settings │ ├── settings.py │ ├── urls.py │ └── wsgi.py ├── converter/ # Main app │ ├── views.py │ ├── urls.py │ ├── templates/converter/ │ │ ├── home.html │ │ ├── result.html │ │ └── loading.html │ └── static/converter/ │ ├── css/ │ │ ├── styles.css # ✨ Enhanced with mobile glow effects │ │ └── loading.css │ ├── js/ │ │ ├── script.js │ │ ├── pwa.js # 📱 PWA functionality │ │ └── sw.js # Service Worker │ ├── manifest.json # 📱 PWA manifest │ └── logo/ │ └── logo.png ├── media/ # Auto-generated MP3 files ├── requirements.txt └── README.md


---

## 🔧 Installation & Setup

### **Prerequisites**
- Python 3.11+
- FFmpeg installed on system
- Git

### **Local Development**
```bash
# Clone repository
git clone [https://github.com/fredrexsalac/himigtube.git](https://github.com/fredrexsalac/himigtube.git)
cd himigtube

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

Django>=4.2
yt-dlp>=2023.10
ffmpeg-python
youtubesearchpython
requests

Django>=4.2
yt-dlp>=2023.10
ffmpeg-python
youtubesearchpython
requests

📱 Mobile Features
Enhanced Mobile Experience
Glowing Cards - Search results have animated glow effects
Touch-Optimized - Larger buttons and touch targets
Smooth Animations - Buttery smooth transitions and hover effects
Responsive Layout - Adapts perfectly to all screen sizes
PWA Installation - Install as native app for better performance
Mobile-Specific Animations
mobile-glow - Pulsing glow effect for result cards
button-glow - Animated glow for convert buttons
Enhanced hover states with scaling effects
Gradient backgrounds with transparency
🎨 Design Features
Color Scheme
Primary: Pink gradients (#ff6b9d to #c44569)
Secondary: Philippines flag colors
Accents: White with transparency effects
Mobile: Enhanced with glow effects and stronger contrasts
Typography
Font Family: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
Headings: Bold with text shadows
Mobile: Uppercase styling for buttons with letter spacing
🛡 Disclaimer
This tool is for personal use only.

We do not host any copyrighted material. All music is fetched dynamically through public YouTube results. Please support original artists by streaming or purchasing their content officially.

🤝 Contributing
Feel free to fork, clone, suggest hugot lines, or improve the UI/UX. Pinoy devs welcome!

Development Setup
bash
git clone https://github.com/fredrexsalac/himigtube.git
cd himigtube
pip install -r requirements.txt
python manage.py runserver
Contributing Guidelines
Fork the repository
Create a feature branch
Make your changes
Test on mobile and desktop
Submit a pull request
📊 Changelog
v2.0.0 - Latest Updates
✅ Added PWA support with mobile app installation
✅ Enhanced navigation tabs with interactive states
✅ Fixed search results display issue
✅ Improved mobile design with glow effects
✅ Code cleanup and performance optimization
v1.0.0 - Initial Release
🎵 Basic YouTube to MP3 conversion
🎨 Filipino-themed design
📱 Mobile responsive layout
💬 Hugot loading messages
🛒 Support the Developer
Support the developer or download the app: 👉 Ko-fi: https://ko-fi.com/s/21732092be

📧 Contact
📬 Ko-fi: ko-fi.com/therealdon
📩 Email: fredrexsalac@gmail.com
🧠 Built with 💙 by [The Real Don] – #PinoyProud
📢 Social Media
"Ever wondered why you're bored? Pagod ka na ba maghanap ng YouTube to MP3 na gumagana? HimigTube na ang sagot! Hugot + Meme + Music = Love. 🇵🇭🎧

Download now. Baka ito na ang closure mo."

Made with ❤️ in the Philippines 🇵🇭

Note:
This updated README.md includes all the major changes we made:
- ✅ PWA functionality and mobile app installation
- ✅ Enhanced UI with navigation tab states
- ✅ Fixed search results display
- ✅ Mobile glow effects and animations
- ✅ Technical improvements and code structure
- ✅ Installation guides for PWA
- ✅ Updated project structure
<<<<<<< HEAD
- ✅ Changelog with version history
=======
- ✅ Changelog with version history
>>>>>>> 9fa374110cd555a6c03f63fcb132411716adcb2e
