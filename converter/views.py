from django.shortcuts import render, redirect
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
from django.conf import settings
import os
import uuid
import re
import traceback

# 🧼 Sanitize file names
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# 🔁 Redirect root URL to loading page
def redirect_to_loading(request):
    return redirect('converter:loading')

# ⏳ Loading screen view
def loading_screen(request):
    return render(request, 'converter/loading.html')

# 🏠 Home / Search view
def home(request):
    query = request.GET.get('query', '').strip()
    results = []

    if query:
        try:
            # 🎧 Improve accuracy for musical searches only
            MUSIC_KEYWORDS = ['music', 'song', 'opm', 'lyrics', 'mp3', 'official', 'cover', 'audio']
            if not any(word in query.lower() for word in MUSIC_KEYWORDS):
                refined_query = f"{query} official music"
            else:
                refined_query = query

            print(f"[Query Used] {refined_query}")  # ✅ Debug

            # 🔍 Perform search
            videos_search = VideosSearch(refined_query, limit=20)
            search_results = videos_search.result().get('result', [])

            for video in search_results:
                results.append({
                    'title': video.get('title', 'Unknown Title'),
                    'url': video.get('link'),
                    'thumbnail': video['thumbnails'][0]['url']
                        if video.get('thumbnails') and len(video['thumbnails']) > 0 else '',
                    'duration': video.get('duration', 'N/A'),
                })

        except Exception as e:
            print(f"[Search Error] {e}")
            traceback.print_exc()
            results = []

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

# 📄 Result page (optional)
def result(request):
    return render(request, 'converter/result.html')

# 🔁 MP3 conversion process
def process(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        bitrate = request.POST.get("bitrate", "192")

        if not video_url:
            return redirect("converter:home")

        try:
            unique_id = str(uuid.uuid4())[:8]
            output_template = os.path.join(settings.MEDIA_ROOT, f"%(title)s_{unique_id}.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'cookiefile': os.path.join(settings.BASE_DIR, 'converter', 'yt_cookies.txt'),  # 👈 Add this line
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'quiet': True,
                'noplaylist': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = sanitize_filename(info.get("title", "Unknown"))
                filename = f"{title}_{unique_id}.mp3"
                download_url = f"{settings.MEDIA_URL}{filename}"
                thumbnail = info.get("thumbnail", "")

        except Exception as e:
            print(f"[Download Error] {e}")
            traceback.print_exc()
            return render(request, "converter/result.html", {
                "title": "Error",
                "download_url": None,
                "error": "❌ Failed to process the video. Please try again.",
                "thumbnail": "",
            })

        return render(request, "converter/result.html", {
            "title": title,
            "download_url": download_url,
            "thumbnail": thumbnail
        })

    return redirect("converter:home")
