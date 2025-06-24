# Social Downloader SaaS (MVP)

A simple SaaS tool to download videos from multiple platforms (YouTube, Instagram, TikTok, X, Facebook) and generate AI captions with multilingual support.

## Features
- Download video/audio in various formats
- Generate auto-captions with Whisper
- Translate captions to multiple languages
- Clean, ad-free interface using TailwindCSS + HTMX

## Stack
- Backend: Django + PostgreSQL
- Frontend: TailwindCSS, HTMX
- AI: Whisper / OpenAI / DeepL

## Setup
```bash
uv venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver