from django.shortcuts import render
from django.http import HttpResponse
import yt_dlp
import os
from .helper import extract_audio, transcribe_audio
from .tasks import download_video_task
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import FileResponse
from django.template.loader import render_to_string
import pprint

from celery.result import AsyncResult
from celery_progress.backend import Progress
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'downloader/home.html')



SUPPORTED_SITES = [
    "youtube.com",
     "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com", 
    "fb.watch",
    "x.com", 
    "twitter.com"
]

def is_valid_video_url(url):
    return any(site in url for site in SUPPORTED_SITES)


@require_POST
def get_url(request):
    
    url = request.POST.get("url")
    if not is_valid_video_url(url):
        return HttpResponse("<p class='text-red-600'>Invalid video URL. Only YouTube, TikTok, Instagram, X, Facebook are supported.</p>")
    title, thumbnail, formats = get_video_formats(url)

    return render(request, "partials/preview_card.html", {
        "url": url,
        "title": title,
        "thumbnail": thumbnail,
        "formats": formats,
    })
   


def get_video_formats(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
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
   
     format_id = request.POST.get("format_id")
     url = request.POST.get("url")
     output_dir = "downloads"
     os.makedirs(output_dir, exist_ok=True)
     extract_audio_flag = request.POST.get("extract_audio") == "1"
     generate_transcript_flag = request.POST.get("generate_transcript") == "1"
     print("▶️ Download URL:", url)
     print("📺 Format ID:", format_id)

     ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

     try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "video")
        # Feature 1: Extract Audio
        audio_path = None
        if extract_audio_flag:
            audio_path = extract_audio(filename)

        # Feature 2: Generate Transcript
        transcript = None
        if generate_transcript_flag and audio_path:
            transcript = transcribe_audio(audio_path)

        messages = [f"✅ Downloaded: <strong>{title}</strong>"]
        if extract_audio_flag:
            messages.append("🎵 Audio extracted.")
        if generate_transcript_flag and transcript:
            messages.append("📄 Transcript generated.")

        return render(
                request,
                'partials/download_success.html',
                {
                    "info":info,
                    'filename':filename,
                    'transcript':transcript,
                    'messages':messages
                }
            )
            
        
     except Exception as e:
        print(f"Download error", e)
        return HttpResponse("<p class='text-red-600'>Download failed.</p>")
     

