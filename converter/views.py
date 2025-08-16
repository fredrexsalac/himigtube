from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
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
            results = []

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

def result(request):
    return render(request, 'converter/result.html')

def process(request):
    if request.method != "POST":
        return redirect("converter:home")

    video_id = request.POST.get("video_id")
    if not video_id:
        return redirect("converter:home")

    if not cookies_exist():
        return render(request, "converter/result.html", {
            "title": "Download Failed",
            "download_url": "",
            "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
            "duration": "",
            "success": False,
            "error": "❌ Cookies not found. Please export your YouTube cookies to cookies.txt.",
        })

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    output_dir = get_output_dir()
    temp_filename = f"{uuid.uuid4()}.%(ext)s"
    output_path = os.path.join(output_dir, temp_filename)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": False,  # Show progress in console
        "no_warnings": True,
        "cookiefile": "cookies.txt",  
        "nocheckcertificate": True,    
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title", "Unknown Title")
            ext = info.get('ext', 'mp3')
            downloaded_file = os.path.join(output_dir, f"{info.get('id')}.{ext}")

            # Fallback if default path fails
            if not os.path.exists(downloaded_file):
                downloaded_file = output_path.replace("%(ext)s", "mp3")

        return FileResponse(
            open(downloaded_file, "rb"),
            as_attachment=True,
            filename=f"{sanitize_filename(title)}.mp3"
        )

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"[yt-dlp ERROR]: {e}")
        return render(request, "converter/result.html", {
            "title": "Download Failed",
            "download_url": "",
            "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
            "duration": "",
            "success": False,
            "error": f"❌ Download failed. YouTube may require login. Make sure your cookies.txt is valid. Error: {str(e)}",
        })

    except Exception as e:
        logger.error(f"[GENERAL ERROR]: {e}")
        return render(request, "converter/result.html", {
            "title": "Download Failed",
            "download_url": "",
            "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
            "duration": "",
            "success": False,
            "error": "❌ Conversion failed. Please try again.",
        })
