from django.shortcuts import render, redirect
from youtubesearchpython import VideosSearch
from django.http import FileResponse, HttpResponse
import os, uuid, re, yt_dlp

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def redirect_to_loading(request):
    return redirect('converter:loading')

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

    return render(request, 'converter/home.html', {
        'results': results,
        'query': query,
    })

def result(request):
    return render(request, 'converter/result.html')

def process(request):
    if request.method == "POST":
        video_id = request.POST.get("video_id")

        if not video_id:
            return redirect("converter:home")

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 🔥 Output path (temporary folder for downloads)
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)

        # Random filename to avoid collisions
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(output_dir, filename)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.replace(".mp3", ".%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get("title", "Unknown Title")

                # yt-dlp replaces ext → fix final path
                final_file = output_path
                if os.path.exists(output_path.replace(".mp3", ".webm")):
                    final_file = output_path.replace(".mp3", ".webm")
                elif os.path.exists(output_path.replace(".mp3", ".m4a")):
                    final_file = output_path.replace(".mp3", ".m4a")

                final_file = final_file.replace(".webm", ".mp3").replace(".m4a", ".mp3")

            # ✅ Return downloadable file
            return FileResponse(
                open(final_file, "rb"),
                as_attachment=True,
                filename=f"{sanitize_filename(title)}.mp3"
            )

        except Exception as e:
            print(f"[yt-dlp ERROR]: {e}")
            return render(request, "converter/result.html", {
                "title": "Download Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": "❌ Conversion failed. Please try again.",
            })

    return redirect("converter:home")
