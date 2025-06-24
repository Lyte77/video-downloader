from django.shortcuts import render
from django.http import HttpResponse
import yt_dlp
import os
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
    # try:
    #     with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
    #         info = ydl.extract_info(url, download=False)
    #         # context = {
    #         #     'title': info['title'],
    #         #     'thumbnail': info['thumbnail'],
    #         #     'video_id': info['id']
    #         # }
    #         title, thumbnail, formats = get_video_formats(url)
    #         context = {
    #             "title": title,
    #             "thumbnail": thumbnail,
    #             "formats": formats,
    #             "url": url
    #     }

    #         return render(request, "partials/preview_card.html", context)

    # except Exception:
    #     return HttpResponse("<p class='text-red-600'>Failed to load video info.</p>")
    


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
     video_id = request.POST.get("video_id")
     url = f"https://www.youtube.com/watch?v={video_id}"
     output_dir = "downloads"
     os.makedirs(output_dir, exist_ok=True)

     ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

     try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return FileResponse(
                open(filename, 'rb'),
                as_attachment=True,  
                filename=os.path.basename(filename)  
            )
     except Exception:
        return HttpResponse("<p class='text-red-600'>Download failed.</p>")
     

def get_progress(request, task_id):
    progress = Progress(AsyncResult(task_id))
    value = int(progress.get_info()['progress']['percent'])

    if value == 100:
        return render(request, 'partials/success.html', {"message": "✅ Download complete!"})

    return render(request, 'partials/progress_bar.html', {"value": value})
