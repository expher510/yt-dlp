import yt_dlp, os

url = os.environ.get("VIDEO_URL")
print(f"URL received: {url}")  # أضف السطر ده

if not url:
    raise ValueError("❌ VIDEO_URL is empty!")

ydl_opts = {
    'format': 'best[ext=mp4]',
    'outtmpl': '/tmp/%(title)s.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    print(f"✅ Downloaded: {info['title']}")
