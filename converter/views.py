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
        bitrate = request.POST.get("bitrate", "192")

        if not video_url:
            return redirect("converter:home")

        unique_id = str(uuid.uuid4())[:8]
        outtmpl = os.path.join(settings.MEDIA_ROOT, f"%(title)s_{unique_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            }],
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = sanitize_filename(info.get("title", "Unknown"))
            file_name = f"{title}_{unique_id}.mp3"
            download_url = f"{settings.MEDIA_URL}{file_name}"

        return render(request, "converter/result.html", {
            "title": title,
            "download_url": download_url,
            "thumbnail": info.get("thumbnail", "")
        })

    return redirect("converter:home")
