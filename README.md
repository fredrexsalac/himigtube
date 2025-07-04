# 🎶 HimigTube - Pinoy YouTube to MP3 Converter 🇵🇭

**HimigTube** is a Filipino-themed YouTube to MP3 downloader built using Django + yt-dlp + FFmpeg, designed especially for music lovers who want to convert YouTube songs directly into downloadable MP3 files — all wrapped in a vibrant, Pinoy-inspired experience with hugot feels, loading animations, and progressive processing UI.

> 📅 Released: 2025  
> 💻 Built by: A Computer Science student from the Philippines  
> 🛠 Hosted on: Render + GitHub  
> 🌍 Website: [https://himigtube.render.com](#)

---

## 🚀 Features

- 🎧 Search any YouTube music using title, artist, or lyrics.
- 🔄 Converts YouTube audio to MP3 with customizable bitrate options.
- 💬 Displays funny hugot-style comments during processing.
- 🌀 Progress bar with animation and meme GIFs to entertain users.
- 📥 Automatic download after conversion.
- 📱 Fully responsive for mobile, tablet, and desktop.
- 🎨 Filipino-inspired design (colors, fonts, banners).
- 🧼 Optional meme GIF like *Cat Laundry* while loading.

---

## 📷 UI Screenshots

- 🔍 Search Page
- 📊 Loading Page (with animated hugot lines)
- ✅ Result Page with Auto-Download
- 🪟 About Modal with logo, disclaimer, and guide

---

## 🔧 How It Works

1. **User searches a song** — using any keyword like “KZ Tandingan Labo” or “Parokya ni Edgar Buloy”.
2. **System uses youtubesearchpython** to fetch the most accurate videos from YouTube.
3. **User selects desired song** and bitrate, then clicks **"Convert to MP3"**.
4. **A loading screen appears** — complete with a progress bar, hugot lines, and a meme.
5. **Conversion is handled using `yt-dlp` + `FFmpeg`**, saving the MP3 file into `media/`.
6. **Once done**, it triggers an auto-download in the user’s browser.

---

## 🛠 Built With

- Python 3.11+
- Django 4.x
- yt-dlp
- FFmpeg
- HTML5, CSS3, JavaScript
- Bootstrap (minimal)
- Tenor GIF embeds
- Render.com (for deployment)
- GitHub (for source code + versioning)

---

## 📂 Project Structure

himigtube/
├── himigtube/ # Django project settings
│ ├── settings.py
│ ├── urls.py
├── converter/ # Main app
│ ├── views.py
│ ├── urls.py
│ ├── templates/converter/
│ │ ├── home.html
│ │ ├── result.html
│ │ ├── loading.html
│ ├── static/converter/
│ │ ├── css/
│ │ │ ├── styles.css
│ │ │ ├── loading.css
│ │ ├── js/
│ │ ├── logo/
│ │ │ └── logo.png
├── media/ # Auto-generated MP3 files
├── requirements.txt
├── README.md

----


---

## 📄 Requirements

```bash
Django>=4.2
yt-dlp>=2023.10
ffmpeg
youtubesearchpython
```
---
🛡 Disclaimer
This tool is for personal use only.

We do not host any copyrighted material.
All music is fetched dynamically through public YouTube results. Please support original artists by streaming or purchasing their content officially.

🤝 Contribution
Feel free to fork, clone, suggest hugot lines, or improve the UI/UX. Pinoy devs welcome!

bash
Copy
Edit
git clone https://github.com/fredrexsalac/himigtube.git
Then run:

bash
Copy
Edit
pip install -r requirements.txt
python manage.py runserver
🛒 Ko-fi Product Page
Support the developer or download the app:
👉 https://ko-fi.com/s/21732092be

📢 Social Media Caption (optional)
"Ever wondered why you're bored? Pagod ka na ba maghanap ng YouTube to MP3 na gumagana? HimigTube na ang sagot! Hugot + Meme + Music = Love. 🇵🇭🎧
Download now. Baka ito na ang closure mo."

📧 Contact
📬 ko-fi.com/yourname
📩 Email: himigtube@gmail.com
🧠 Built with 💙 by [The Real Don] – #PinoyProud


---

Let me know if you'd like a markdown badge version or a simpler Ko-fi promo layout.
