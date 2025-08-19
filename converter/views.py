from django.shortcuts import render, redirect
from youtubesearchpython import VideosSearch
from django.conf import settings
import os, uuid, re, requests

# ✅ Your RapidAPI credentials
RAPIDAPI_KEY = "52e6b02768msh62880254bc3809fp1f4474jsn915acd488aaa"
RAPIDAPI_HOST = "youtube-mp36.p.rapidapi.com"

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
                'video_id': video_id,  # ✅ store this for conversion
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

        # ✅ Call RapidAPI to convert
        url = f"https://{RAPIDAPI_HOST}/dl"
        querystring = {"id": video_id}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        try:
            r = requests.get(url, headers=headers, params=querystring)
            data = r.json()

            if "link" in data and data["link"]:
                return render(request, "converter/result.html", {
                    "title": data.get("title", "Unknown"),
                    "download_url": data["link"],
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    "duration": data.get("duration", ""),
                    "success": True,
                })
            else:
                return render(request, "converter/result.html", {
                    "title": "Download Failed",
                    "download_url": "",
                    "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                    "duration": "",
                    "success": False,
                    "error": "❌ Conversion failed. Please try again.",
                })

        except Exception as e:
            print(f"[RapidAPI ERROR]: {e}")
            return render(request, "converter/result.html", {
                "title": "Download Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": "❌ API error. Please try again later.",
            })

    return redirect("converter:home")
