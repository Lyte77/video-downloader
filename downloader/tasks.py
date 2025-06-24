# downloader/tasks.py
from celery import shared_task
from celery_progress.backend import ProgressRecorder
import yt_dlp

@shared_task(bind=True)
def download_video_task(self, url, format_id):
    progress_recorder = ProgressRecorder(self)

    ydl_opts = {
        "format": format_id,
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "progress_hooks": [lambda d: progress_recorder.set_progress(d.get('_percent_str', 0), 100)],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    return info.get("title", "Download complete")
