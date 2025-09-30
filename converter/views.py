from django.shortcuts import render, redirect
from youtubesearchpython import VideosSearch
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, FileResponse, JsonResponse
from collections import Counter
import os, uuid, re, requests, subprocess, tempfile, json


RAPIDAPI_KEY = "52e6b02768msh62880254bc3809fp1f4474jsn915acd488aaa"
RAPIDAPI_HOST = "youtube-mp36.p.rapidapi.com"

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def is_kids_content(title):
    """Filter out kids songs and children's content"""
    kids_keywords = [
        'kids', 'children', 'nursery', 'rhyme', 'baby', 'toddler', 'preschool',
        'kindergarten', 'cartoon', 'disney junior', 'cocomelon', 'peppa pig',
        'paw patrol', 'bluey', 'sesame street', 'barney', 'dora', 'mickey mouse',
        'educational', 'learning', 'abc song', 'counting', 'alphabet', 'lullaby',
        'bedtime', 'story time', 'finger family', 'wheels on the bus', 'twinkle',
        'old macdonald', 'bingo', 'head shoulders', 'if you\'re happy', 'itsy bitsy'
    ]
    
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in kids_keywords)

def is_movie_content(title):
    """Filter out movie trailers, teasers, and movie-related content"""
    movie_keywords = [
        'trailer', 'teaser', 'official trailer', 'movie trailer', 'film trailer',
        'coming soon', 'sneak peek', 'first look', 'behind the scenes', 'making of',
        'movie clip', 'film clip', 'exclusive clip', 'extended trailer', 'final trailer',
        'international trailer', 'red band trailer', 'green band trailer', 'tv spot',
        'featurette', 'promo', 'preview', 'movie review', 'film review', 'reaction',
        'breakdown', 'analysis', 'explained', 'ending explained', 'easter eggs',
        'deleted scene', 'bloopers', 'gag reel', 'outtakes', 'press conference',
        'interview', 'premiere', 'red carpet', 'movie news', 'casting news'
    ]
    
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in movie_keywords)

def is_live_content(title):
    """Filter out live videos and streaming content"""
    live_keywords = [
        'live', 'livestream', 'live stream', 'streaming', 'stream', 'live now',
        'live performance', 'live concert', 'live show', 'live session',
        'live recording', 'live version', 'live at', 'concert', 'tour',
        'festival', 'live broadcast', 'streaming now', 'going live',
        'live music', 'acoustic session', 'unplugged', 'live acoustic',
        'live cover', 'jam session', 'live rehearsal', 'soundcheck'
    ]
    
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in live_keywords)

def add_to_search_history(request, query):
    """Add search query to user's session-based search history"""
    if not query or len(query.strip()) < 2:
        return
    
    # Get existing search history from session
    search_history = request.session.get('search_history', [])
    
    # Clean and normalize the query
    clean_query = query.strip().lower()
    
    # Remove if already exists (to move it to front)
    search_history = [q for q in search_history if q.lower() != clean_query]
    
    # Add to front of list
    search_history.insert(0, query.strip())
    
    # Keep only last 20 searches
    search_history = search_history[:20]
    
    # Save back to session
    request.session['search_history'] = search_history
    request.session.modified = True

def extract_artists_from_history(search_history):
    """Extract potential artist names from search history"""
    artists = []
    common_music_words = ['official', 'music', 'video', 'mv', 'audio', 'song', 'lyrics', 'live', 'cover', 'remix']
    
    for query in search_history:
        # Split query and filter out common music words
        words = query.lower().split()
        potential_artists = [word for word in words if word not in common_music_words and len(word) > 2]
        
        # Take first 2-3 words as potential artist names
        artists.extend(potential_artists[:3])
    
    return artists

def get_personalized_recommendations(request):
    """Generate recommendations based on user's search history"""
    search_history = request.session.get('search_history', [])
    
    if not search_history:
        return []
    
    recommendations = []
    
    try:
        # Extract artists/keywords from search history
        artists = extract_artists_from_history(search_history)
        
        # Count frequency of artists/keywords
        artist_counts = Counter(artists)
        top_artists = [artist for artist, count in artist_counts.most_common(5)]
        
        # Generate recommendation queries based on search patterns
        recommendation_queries = []
        
        # Use recent searches directly
        for query in search_history[:3]:
            recommendation_queries.append(f"{query} similar artists")
            recommendation_queries.append(f"{query} related songs")
        
        # Use top artists
        for artist in top_artists[:3]:
            recommendation_queries.append(f"{artist} popular songs")
            recommendation_queries.append(f"{artist} latest music")
        
        # Search for recommendations
        for query in recommendation_queries[:6]:  # Limit queries to avoid too many API calls
            try:
                videos_search = VideosSearch(query, limit=5)
                results_data = videos_search.result().get('result', [])
                
                for video in results_data:
                    if len(recommendations) >= 15:  # Limit total recommendations
                        break
                        
                    video_id = video.get('id')
                    title = video.get('title', 'Unknown Title')
                    link = f"https://www.youtube.com/watch?v={video_id}"
                    thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                    duration = video.get('duration', 'N/A')
                    
                    # Filter for music-related content, exclude kids content, exclude movie content, exclude live content, and exclude album content
                    if (any(keyword in title.lower() for keyword in ['music', 'official', 'mv', 'video', 'song', 'audio']) and
                        not is_kids_content(title) and
                        not is_movie_content(title) and
                        not is_live_content(title) and
                        not any(keyword in title.lower() for keyword in ['album', 'discography', 'playlist'])):
                        # Avoid duplicates
                        if not any(rec['video_id'] == video_id for rec in recommendations):
                            recommendations.append({
                                'title': title,
                                'url': link,
                                'video_id': video_id,
                                'thumbnail': thumbnail,
                                'duration': duration,
                                'source': 'personalized'
                            })
                
                if len(recommendations) >= 12:
                    break
                    
            except Exception as e:
                print(f"[PERSONALIZED RECOMMENDATION ERROR]: {e}")
                continue
                
    except Exception as e:
        print(f"[PERSONALIZED RECOMMENDATIONS ERROR]: {e}")
    
    return recommendations

def get_recommended_songs(request=None):
    """Fetch trending Filipino songs + personalized recommendations based on search history"""
    recommended = []
    
    # First, get personalized recommendations if user has search history
    if request:
        search_history = request.session.get('search_history', [])
        if search_history:
            try:
                # Extract artists/keywords from search history
                artists = extract_artists_from_history(search_history)
                
                # Count frequency of artists/keywords
                artist_counts = Counter(artists)
                top_artists = [artist for artist, count in artist_counts.most_common(3)]
                
                # Generate recommendation queries based on search patterns
                recommendation_queries = []
                
                # Use recent searches directly
                for query in search_history[:2]:
                    recommendation_queries.append(f"{query} popular songs")
                    recommendation_queries.append(f"{query} similar artists")
                
                # Use top artists
                for artist in top_artists[:2]:
                    recommendation_queries.append(f"{artist} best songs")
                
                # Search for personalized recommendations
                for query in recommendation_queries[:4]:  # Limit to avoid too many API calls
                    try:
                        videos_search = VideosSearch(query, limit=3)
                        results_data = videos_search.result().get('result', [])
                        
                        for video in results_data:
                            if len(recommended) >= 6:  # Reserve space for Filipino songs
                                break
                                
                            video_id = video.get('id')
                            title = video.get('title', 'Unknown Title')
                            link = f"https://www.youtube.com/watch?v={video_id}"
                            thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                            duration = video.get('duration', 'N/A')
                            
                            # Filter for music-related content, exclude kids content, exclude movie content, exclude live content, and exclude album content
                            if (any(keyword in title.lower() for keyword in ['music', 'official', 'mv', 'video', 'song', 'audio']) and
                                not is_kids_content(title) and
                                not is_movie_content(title) and
                                not is_live_content(title) and
                                not any(keyword in title.lower() for keyword in ['album', 'discography', 'playlist'])):
                                # Avoid duplicates
                                if not any(rec['video_id'] == video_id for rec in recommended):
                                    recommended.append({
                                        'title': title,
                                        'url': link,
                                        'video_id': video_id,
                                        'thumbnail': thumbnail,
                                        'duration': duration,
                                        'source': 'personalized'
                                    })
                        
                        if len(recommended) >= 6:
                            break
                            
                    except Exception as e:
                        print(f"[PERSONALIZED RECOMMENDATION ERROR]: {e}")
                        continue
                        
            except Exception as e:
                print(f"[SEARCH HISTORY ERROR]: {e}")
    
    # Then, add Filipino trending songs to fill the rest
    try:
        # Only use fallback songs if no personalized recommendations exist
        if len(recommended) == 0:
            # Fallback to manual popular Filipino songs
            fallback_songs = [
                "Ben&Ben Leaves official music video",
                "SB19 GENTO official music video", 
                "BINI Pantropiko official music video",
                "Moira Dela Torre Paubaya official music video",
                "December Avenue Kung Di Rin Lang Ikaw official music video"
            ]
            
            for song in fallback_songs:
                if len(recommended) >= 12:
                    break
                try:
                    videos_search = VideosSearch(song, limit=1)
                    results_data = videos_search.result().get('result', [])
                    
                    if results_data:
                        video = results_data[0]
                        video_id = video.get('id')
                        title = video.get('title', 'Unknown Title')
                        link = f"https://www.youtube.com/watch?v={video_id}"
                        thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                        duration = video.get('duration', 'N/A')
                        
                        # Filter for music-related content, exclude kids content, exclude movie content, exclude live content, and exclude album content
                        if (any(keyword in title.lower() for keyword in ['music', 'official', 'mv', 'video', 'song', 'audio']) and
                            not is_kids_content(title) and
                            not is_movie_content(title) and
                            not is_live_content(title) and
                            not any(keyword in title.lower() for keyword in ['album', 'discography', 'playlist']) and
                            not any(rec['video_id'] == video_id for rec in recommended)):
                            recommended.append({
                                'title': title,
                                'url': link,
                                'video_id': video_id,
                                'thumbnail': thumbnail,
                                'duration': duration,
                                'source': 'filipino_fallback'
                            })
                except:
                    continue
                    
    except Exception as e:
        print(f"[RECOMMENDED SONGS ERROR]: {e}")
    
    return recommended[:12]  # Return max 12 recommendations

def get_discovery_recommendations():
    """Get global and Filipino artists music recommendations for discovery"""
    discovery_songs = []
    
    # Popular Filipino Artists
    filipino_artists = [
        "Ben&Ben", "SB19", "BINI", "Moira Dela Torre", "December Avenue",
        "IV of Spades", "The Juans", "Zack Tabudlo", "Arthur Nery", "Lola Amour",
        "Munimuni", "Cup of Joe", "Sponge Cola", "Parokya ni Edgar", "Eraserheads",
        "Rivermaya", "Bamboo", "Kamikazee", "Silent Sanctuary", "Callalily"
    ]
    
    # Popular Global Artists
    global_artists = [
        "Taylor Swift", "Ed Sheeran", "Billie Eilish", "Dua Lipa", "The Weeknd",
        "Bruno Mars", "Ariana Grande", "Post Malone", "Olivia Rodrigo", "Harry Styles",
        "BTS", "BLACKPINK", "NewJeans", "IVE", "Stray Kids",
        "Maroon 5", "Imagine Dragons", "OneRepublic", "Coldplay", "Charlie Puth"
    ]
    
    try:
        # Get 3 Filipino artists and 3 global artists randomly
        import random
        selected_filipino = random.sample(filipino_artists, min(3, len(filipino_artists)))
        selected_global = random.sample(global_artists, min(3, len(global_artists)))
        
        all_selected_artists = selected_filipino + selected_global
        
        for artist in all_selected_artists:
            if len(discovery_songs) >= 12:  # Limit total recommendations
                break
                
            try:
                # Search for popular songs by this artist
                search_query = f"{artist} popular songs official music video"
                videos_search = VideosSearch(search_query, limit=2)
                results_data = videos_search.result().get('result', [])
                
                for video in results_data:
                    if len(discovery_songs) >= 12:
                        break
                        
                    video_id = video.get('id')
                    title = video.get('title', 'Unknown Title')
                    link = f"https://www.youtube.com/watch?v={video_id}"
                    thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                    duration = video.get('duration', 'N/A')
                    
                    # Filter for music-related content and exclude unwanted content
                    if (any(keyword in title.lower() for keyword in ['music', 'official', 'mv', 'video', 'song', 'audio']) and
                        not is_kids_content(title) and
                        not is_movie_content(title) and
                        not is_live_content(title) and
                        not any(keyword in title.lower() for keyword in ['album', 'discography', 'playlist'])):
                        
                        # Avoid duplicates
                        if not any(rec['video_id'] == video_id for rec in discovery_songs):
                            artist_type = 'filipino' if artist in filipino_artists else 'global'
                            discovery_songs.append({
                                'title': title,
                                'url': link,
                                'video_id': video_id,
                                'thumbnail': thumbnail,
                                'duration': duration,
                                'artist': artist,
                                'artist_type': artist_type,
                                'source': 'discovery'
                            })
                            
            except Exception as e:
                print(f"[DISCOVERY RECOMMENDATION ERROR for {artist}]: {e}")
                continue
                
    except Exception as e:
        print(f"[DISCOVERY RECOMMENDATIONS ERROR]: {e}")
    
    return discovery_songs
    
def redirect_to_loading(request):
    return redirect('converter:loading')

def loading_screen(request):
    return render(request, 'converter/loading.html')

def home(request):
    query = request.GET.get('query', '')
    results = []
    recommended_songs = []
    personalized_recommendations = []
    discovery_recommendations = []

    if query:
        refined_query = f"{query} official music"
        videos_search = VideosSearch(refined_query, limit=30)
    if query:
        refined_query = f"{query} official music"
        videos_search = VideosSearch(refined_query, limit=20)
        results_data = videos_search.result().get('result', [])

        for video in results_data:
            video_id = video.get('id')
            title = video.get('title', 'Unknown Title')
            link = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail = video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
            duration = video.get('duration', 'Unknown')
            
            # Filter out kids content, movie trailers, and live content
            if not is_kids_content(title) and not is_movie_content(title) and not is_live_content(title):
                results.append({
                    'video_id': video_id,
                    'title': title,
                    'link': link,
                    'thumbnail': thumbnail,
                    'duration': duration,
                })
            
            # Stop when we have 10 relevant results
            if len(results) >= 10:
                break
        
        # Add query to search history
        add_to_search_history(request, query)
        
        # Get personalized recommendations
        personalized_recommendations = get_personalized_recommendations(request)
        discovery_recommendations = get_discovery_recommendations()
    
    else:
        # Show recommended songs when no search query
        recommended_songs = get_recommended_songs(request)
        personalized_recommendations = get_personalized_recommendations(request)
        discovery_recommendations = get_discovery_recommendations()

    return render(request, 'converter/home.html', {
        'results': results,
        'recommended_songs': recommended_songs,
        'personalized_recommendations': personalized_recommendations,
        'discovery_recommendations': discovery_recommendations,
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
        url = f"https://{RAPIDAPI_HOST}/dl"
        querystring = {"id": video_id}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        try:
            # Extended timeout for slow internet connections (60 seconds)
            r = requests.get(url, headers=headers, params=querystring, timeout=60)
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
                    "error": " Conversion failed. Please try again.",
                })

        except requests.exceptions.Timeout:
            print(f"[TIMEOUT ERROR]: Request timed out for video_id: {video_id}")
            return render(request, "converter/result.html", {
                "title": "Connection Timeout",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " Connection timeout. Your internet might be slow. Please try again.",
            })
        except requests.exceptions.ConnectionError:
            print(f"[CONNECTION ERROR]: Network connection failed for video_id: {video_id}")
            return render(request, "converter/result.html", {
                "title": "Connection Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " Network connection failed. Check your internet and try again.",
            })
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
                "error": " API error. Please try again later.",
            })

    return redirect("converter:home")

def search_suggestions(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        # Get search suggestions from YouTube
        videos_search = VideosSearch(query, limit=8)
        results_data = videos_search.result().get('result', [])
        
        suggestions = []
        for video in results_data:
            title = video.get('title', '')
            
            # Filter for music content and exclude unwanted content
            if (any(keyword in title.lower() for keyword in ['music', 'official', 'mv', 'video', 'song', 'audio']) and
                not is_kids_content(title) and
                not is_movie_content(title) and
                not is_live_content(title)):
                
                # Extract artist and song from title
                clean_title = re.sub(r'\s*\(.*?\)\s*', '', title)  # Remove parentheses
                clean_title = re.sub(r'\s*\[.*?\]\s*', '', clean_title)  # Remove brackets
                clean_title = re.sub(r'\s*(official|music|video|mv|audio|song)\s*', '', clean_title, flags=re.IGNORECASE)
                
                suggestions.append({
                    'title': clean_title.strip(),
                    'original_title': title,
                    'video_id': video.get('id'),
                    'thumbnail': video.get('thumbnails')[0]['url'] if video.get('thumbnails') else ''
                })
                
                if len(suggestions) >= 6:  # Limit suggestions
                    break
        
        return JsonResponse({'suggestions': suggestions})
        
    except Exception as e:
        print(f"[SEARCH SUGGESTIONS ERROR]: {e}")
        return JsonResponse({'suggestions': []})

def process_video_to_mp3(video_path, output_path):
    """Convert video file to MP3 using FFmpeg"""
    try:
        # FFmpeg command to convert video to MP3
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'mp3',
            '-ab', '192k',  # Audio bitrate
            '-ar', '44100',  # Audio sample rate
            '-y',  # Overwrite output file
            output_path
        ]
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Conversion successful"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except FileNotFoundError:
        return False, "FFmpeg not found. Please install FFmpeg."
    except Exception as e:
        return False, f"Conversion error: {str(e)}"

def video_upload(request):
    """Handle video file upload and conversion to MP3"""
    if request.method == "POST":
        video_file = request.FILES.get('video_file')
        
        if not video_file:
            return render(request, "converter/result.html", {
                "title": "Upload Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " No video file uploaded. Please select a video file.",
            })
        
        # Check file size (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if video_file.size > max_size:
            return render(request, "converter/result.html", {
                "title": "Upload Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " File too large. Maximum size is 100MB.",
            })
        
        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.3gp', '.webm']
        file_ext = os.path.splitext(video_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return render(request, "converter/result.html", {
                "title": "Upload Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " Unsupported file format. Please use MP4, AVI, MOV, MKV, WMV, FLV, 3GP, or WEBM.",
            })
        
        try:
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            original_name = os.path.splitext(video_file.name)[0]
            sanitized_name = sanitize_filename(original_name)
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded video
                video_filename = f"{unique_id}_input{file_ext}"
                video_path = os.path.join(temp_dir, video_filename)
                
                with open(video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                
                # Convert to MP3
                mp3_filename = f"{sanitized_name}_{unique_id}.mp3"
                mp3_path = os.path.join(temp_dir, mp3_filename)
                
                success, message = process_video_to_mp3(video_path, mp3_path)
                
                if success and os.path.exists(mp3_path):
                    # Save MP3 to media directory
                    media_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
                    os.makedirs(media_dir, exist_ok=True)
                    
                    final_mp3_path = os.path.join(media_dir, mp3_filename)
                    
                    # Copy converted file to media directory
                    import shutil
                    shutil.copy2(mp3_path, final_mp3_path)
                    
                    # Generate download URL
                    download_url = f"{settings.MEDIA_URL}converted/{mp3_filename}"
                    
                    return render(request, "converter/result.html", {
                        "title": f"{sanitized_name}",
                        "download_url": download_url,
                        "thumbnail": "https://i.imgur.com/8pTSvjV.png",  # Generic music icon
                        "duration": "Unknown",
                        "success": True,
                        "is_video_conversion": True,
                    })
                else:
                    return render(request, "converter/result.html", {
                        "title": "Conversion Failed",
                        "download_url": "",
                        "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                        "duration": "",
                        "success": False,
                        "error": f" {message}",
                    })
                    
        except Exception as e:
            print(f"[VIDEO UPLOAD ERROR]: {e}")
            return render(request, "converter/result.html", {
                "title": "Upload Failed",
                "download_url": "",
                "thumbnail": "https://media.tenor.com/IHdlTRsmcS4AAAAC/sad-cat.gif",
                "duration": "",
                "success": False,
                "error": " Upload processing failed. Please try again.",
            })
    
    return redirect("converter:home")
                "error": "❌ API error. Please try again later.",
            })

    return redirect("converter:home")
>>>>>>> 455186ee1e1999f6a82cd6b814f12b63252e2c70
