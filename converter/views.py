from django.shortcuts import render, redirect
from django.http import FileResponse
from youtubesearchpython import VideosSearch
import os
import uuid
import re

RAPIDAPI_KEY = "52e6b02768msh62880254bc3809fp1f4474jsn915acd488aaa"
RAPIDAPI_HOST = "youtube-audio-video-download.p.rapidapi.com"

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

        try:
            # Call RapidAPI
            response = requests.get(
                f"https://{RAPIDAPI_HOST}/geturl",
                params={"video_url": video_url},
                headers={
                    "X-Rapidapi-Key": RAPIDAPI_KEY,
                    "X-Rapidapi-Host": RAPIDAPI_HOST
                },
                timeout=15
            )
            data = response.json()

            # Check if API returned a valid audio link
            audio_url = data.get("audio")
            if not audio_url:
                return render(request, "converter/home.html", {"error": "Download failed: No audio URL returned."})

            # Prepare downloads folder
            output_dir = os.path.join(settings.BASE_DIR, "converter", "downloads")
            os.makedirs(output_dir, exist_ok=True)

            # Generate unique filename
            filename = str(uuid.uuid4()) + ".mp3"
            filepath = os.path.join(output_dir, filename)

            # Download the MP3 file from the API link
            audio_resp = requests.get(audio_url, stream=True)
            if audio_resp.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in audio_resp.iter_content(1024):
                        f.write(chunk)
            else:
                return render(request, "converter/home.html", {"error": "Failed to download the audio file."})

            return render(request, "converter/home.html", {"success": True, "file": filename})

        except requests.exceptions.RequestException as e:
            return render(request, "converter/home.html", {"error": f"API request failed: {str(e)}"})
        except Exception as e:
            return render(request, "converter/home.html", {"error": f"An unexpected error occurred: {str(e)}"})

    return render(request, "converter/home.html")
