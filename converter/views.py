from django.shortcuts import render, redirect
from django.http import FileResponse
from youtubesearchpython import VideosSearch
import os
import uuid
import re
import yt_dlp
import logging

# Set up logging
logger = logging.getLogger(__name__)

# -----------------------------
# Helper functions
# -----------------------------
def sanitize_filename(name):
    """Replace invalid filename characters with underscores."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_output_dir():
    """Ensure the downloads directory exists."""
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def cookies_exist():
    """Check if cookies.txt exists."""
    return os.path.exists("cookies.txt")

# -----------------------------
# Views
# -----------------------------
def redirect_to_loading(request):
    return redirect('converter:loading')

def loading_screen(request):
    return render(request, 'converter/loading.html')

def home(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        refined_query = f"{query} official music"
        try:
            videos_search = VideosSearch(refined_query, limit=20)
            results_data = videos_search.result().get('result', [])

            for video in results_data:
                video_id = video.get('id')
                title = video.get('title', 'Unknown Title')
                link = f"https://www.youtube.com/watch?v={video_id}"
                thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                duration = video.get('duration', 'N/A')

                results.append({
                    'title': title,
                    'url': link,
                    'video_id': video_id,
                    'thumbnail': thumbnail,
                    'duration': duration,
                })

        except Exception as e:
            logger.error(f"Video search failed: {e}")

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

def result(request):
    return render(request, 'converter/result.html')

def process(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        if not video_url:
            return render(request, "converter/home.html", {"error": "Please enter a YouTube URL."})

        # Ensure downloads folder exists
        output_dir = os.path.join(settings.BASE_DIR, "converter", "downloads")
        os.makedirs(output_dir, exist_ok=True)
        
        # Unique temporary filename
        temp_filename = str(uuid.uuid4())
        temp_path = os.path.join(output_dir, temp_filename + ".%(ext)s")

        # yt_dlp options
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": temp_path,
            "nocheckcertificate": True,
            "quiet": True,
            "cookiefile": os.path.join(settings.BASE_DIR, "converter", "cookies.txt"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                # Build actual mp3 file path
                downloaded_file = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"

            if not os.path.isfile(downloaded_file):
                return render(request, "converter/home.html", {"error": "Download failed. File not found."})

            # Provide filename to template for download
            filename = os.path.basename(downloaded_file)
            return render(request, "converter/home.html", {"success": True, "file": filename})

        except yt_dlp.utils.DownloadError as e:
            return render(request, "converter/home.html", {"error": f"Download failed: {str(e)}"})
        except Exception as e:
            return render(request, "converter/home.html", {"error": f"An unexpected error occurred: {str(e)}"})

    return render(request, "converter/home.html")
