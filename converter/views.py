import os
import re
import uuid
import requests
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from yt_dlp import YoutubeDL
from django.conf import settings

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# ✅ Sanitize file names for OS safety
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# ✅ Redirect from `/` to `/loading/`
def redirect_to_loading(request):
    return redirect('converter:loading')

# ✅ Show loading screen
def loading_screen(request):
    return render(request, 'converter/loading.html')

# ✅ Search videos using RapidAPI
def home(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        url = "https://youtube-search-results.p.rapidapi.com/youtube-search/"
        params = {"q": f"{query} official music"}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-search-results.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()

            for video in data.get("items", []):
                if video.get("type") == "video":
                    results.append({
                        "title": video.get("title", "Unknown Title"),
                        "url": f"https://www.youtube.com/watch?v={video.get('id')}",
                        "thumbnail": video.get("bestThumbnail", {}).get("url", ""),
                        "duration": video.get("duration"),
                    })
        except Exception as e:
            print(f"[RAPIDAPI ERROR]: {e}")

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

# ✅ Render result page
def result(request):
    return render(request, 'converter/result.html')

# ✅ Process MP3 conversion
def process(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        bitrate = request.POST.get("bitrate", "128")

        if not video_url:
            return redirect("converter:home")

        unique_id = str(uuid.uuid4())[:8]
        base_outtmpl = os.path.join(settings.MEDIA_ROOT, f"%(title).40s_{unique_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': base_outtmpl,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }
            ],
            'postprocessor_args': ['-ac', '1'],  # ✅ mono audio
            'noplaylist': True,
            'quiet': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'ignoreerrors': True,
            'retries': 3,
            'cachedir': False,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)

            raw_title = info.get("title") or "Unknown"
            title = sanitize_filename(raw_title)

            output_path = None
            if 'requested_downloads' in info and info['requested_downloads']:
                output_path = info['requested_downloads'][0].get('filepath')
            if not output_path:
                output_path = info.get('_filename')

            if not output_path or not output_path.lower().endswith('.mp3'):
                file_name = f"{title}_{unique_id}.mp3"
            else:
                file_name = os.path.basename(output_path)

            download_url = f"{settings.MEDIA_URL}{file_name}"

            return render(request, "converter/result.html", {
                "title": raw_title,
                "download_url": download_url,
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "success": True,
            })

        except Exception as e:
            print(f"[YT-DLP ERROR]: {e}")
            return render(request, "converter/result.html", {
                "title": "Download Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": "❌ Conversion failed. Please try again with a different video or check your connection.",
            })

    return redirect("converter:home")
