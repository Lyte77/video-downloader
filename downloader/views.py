from django.shortcuts import render
import yt_dlp
import mimetypes
from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import os
import json
import uuid

import logging

from django.http import JsonResponse, FileResponse, Http404
from django.conf import settings
from .helper import transcribe_audio
from django.views.decorators.http import require_POST
from django.shortcuts import render

logger = logging.getLogger(__name__)

# Create your views here.





def home(request):
    return render(request, "downloader/home.html")


SUPPORTED_SITES = [
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "fb.watch",
    "x.com",
    "twitter.com",
]


def is_valid_video_url(url):
    try:
        parsed = urlparse(url)
        if not (parsed.scheme and parsed.netloc):
            return False
        return any(site in parsed.netloc for site in SUPPORTED_SITES)
    except Exception:
        return False


@require_POST
def get_url(request):
    url = request.POST.get("url", "").strip()
    # check empty url
    if not url:
        return render(
            request,
            "partials/error_alert.html",
            {
                "message": "Please enter a video URL.",
                "type": "error", 
            },
        )

    # checking domain validity
    if not is_valid_video_url(url):
        return render(
            request,
            "partials/error_alert.html",
            {
                "message": "Invalid or unsupported URL. Only YouTube, TikTok, Instagram, X, and Facebook are supported.",
                "type": "error",
            },
        )

    try:
        title, thumbnail, formats = get_video_formats(url)
        return render(
            request,
            "partials/preview_card.html",
            {
                "url": url,
                "title": title,
                "thumbnail": thumbnail
                or "/static/default-thumbnail.jpg",
                "formats": formats,
            },
        )

    except DownloadError:
        return render(
            request,
            "partials/error_alert.html",
            {
                "message": "Unable to fetch video details. The link may be private or invalid.",
                "type": "error",
            },
        )

    except Exception as e:
        logger.error(f"Error fetching video info: {e}", exc_info=True)
        return render(
            request,
            "partials/error_alert.html",
            {
                "message": "Something went wrong while processing your request. Please try again.",
                "type": "error",
            },
        )


def get_video_formats(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "")
        thumbnail = info.get("thumbnail", "")
        format_id = info.get("format_id", "")
        ext = info.get("ext", "")
        width = info.get("width", "")
        height = info.get("height", "")
        filesize = info.get("filesize") or 0

        # Construct single merged format
        merged_format = {
            "format_id": format_id,
            "ext": ext,
            "resolution": f"{width}x{height}" if width and height else "Unknown",
            "filesize": filesize,
        }

    return title, thumbnail, [merged_format]



def download_video(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

    url = request.POST.get("url")
    print("--- DEBUG START ---")
    print("POST Data:", request.POST)
    
   
    want_video = request.POST.get("download_video") == "1"
    print(f"Want Video? {want_video}")
    want_audio = request.POST.get("extract_audio") == "1"
    want_transcript = request.POST.get("generate_transcript") == "1"

    if not url:
        return JsonResponse({"success": False, "message": "URL is required"}, status=400)

    # Initialize variables to store results
    video_download_url = None
    audio_download_url = None
    transcript_text = None

    try:
        # --- 2. HANDLE VIDEO DOWNLOAD ---
        if want_video:
            print("Starting Video Download Logic...")
            video_id = str(uuid.uuid4())
            ydl_opts_video = {
                "format": "bestvideo+bestaudio/best", # Downloads video + audio merged
                "outtmpl": os.path.join(settings.DOWNLOADS_DIR, f"{video_id}.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True,
                "overwrites": True,
            }

            with YoutubeDL(ydl_opts_video) as ydl:
                info = ydl.extract_info(url, download=True)
                file_ext = info.get("ext")
            
            
            video_download_url = request.build_absolute_uri(f"/download-file/{video_id}/")

        audio_path = None
        print(f"Video URL Generated: {video_download_url}")
        
        if want_audio or want_transcript:
            audio_id = str(uuid.uuid4())
            audio_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(settings.DOWNLOADS_DIR, f"{audio_id}.%(ext)s"),
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "noplaylist": True,
                "quiet": True,
                "overwrites": True,
            }

            with YoutubeDL(audio_opts) as ydl:
                ydl.extract_info(url, download=True)

            # Define the path explicitly as mp3 because of the postprocessor
            audio_path = os.path.join(settings.DOWNLOADS_DIR, f"{audio_id}.mp3")

           
            if want_audio:
                audio_download_url = request.build_absolute_uri(f"/download-file/{audio_id}/")

        # --- 4. HANDLE TRANSCRIPT ---
        if want_transcript and audio_path and os.path.exists(audio_path):
            # Pass the path of the audio we just downloaded to your AI function
            transcript_text = transcribe_audio(audio_path)
            
           
            if not want_audio:
               os.remove(audio_path)

        # --- 5. PREPARE RESPONSE ---
        context = {
            "success": True,
            "transcript_text": transcript_text, 
        }

        response = render(request, 'partials/download_success.html', context)

        # Prepare the data for the client-side JavaScript to trigger downloads
        trigger_data = {}
        if video_download_url:
            trigger_data["videoUrl"] = video_download_url
        if audio_download_url:
            trigger_data["audioUrl"] = audio_download_url

        # Attach the header
        response['HX-Trigger'] = json.dumps({
            "start-download": trigger_data
        })
        print(f"Trigger Data: {trigger_data}")
        return response

    except Exception as e:
        return render(request, 'partials/download_error.html', {"message": str(e)}, status=200)    





def serve_download(request, file_id):
    folder = settings.DOWNLOADS_DIR

    matches = [f for f in os.listdir(folder) if f.startswith(file_id)]
    if not matches:
        raise Http404("File not found")

    filename = matches[0]
    filepath = os.path.join(folder, filename)

    content_type, _ = mimetypes.guess_type(filepath)

    return FileResponse(
        open(filepath, "rb"),
        as_attachment=True,
        filename=filename,
        content_type=content_type
    )