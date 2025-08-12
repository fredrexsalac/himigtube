from django.shortcuts import render, redirect
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
from django.conf import settings
import os, uuid, re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def loading_screen(request):
    return render(request, 'converter/loading.html')

def home(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        refined_query = f"{query} official music"
        videos_search = VideosSearch(refined_query, limit=20)
        results_data = videos_search.result().get('result', [])

        for video in results_data:
            title = video.get('title', 'Unknown Title')
            link = video.get('link')
            thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
            duration = video.get('duration', 'N/A')

            results.append({
                'title': title,
                'url': link,
                'thumbnail': thumbnail,
                'duration': duration,
            })

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

def result(request):
    return render(request, 'converter/result.html')

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
                {   # Step 1: Extract audio to mp3
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                },
                {   # Step 2: Convert to mono audio
                    'key': 'FFmpegAudioConvertor',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                    'nopostoverwrites': False
                }
            ],
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

            # Determine final file path
            output_path = None
            if 'requested_downloads' in info and info['requested_downloads']:
                output_path = info['requested_downloads'][0].get('filepath')
            if not output_path:
                output_path = info.get('_filename')

            if not output_path or not str(output_path).lower().endswith('.mp3'):
                file_name = f"{title}_{unique_id}.mp3"
                output_path = os.path.join(settings.MEDIA_ROOT, file_name)
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
