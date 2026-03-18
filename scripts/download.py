import subprocess
import sys
import os
import glob


def download(url: str, cookies_path: str = "cookies.txt"):
    if not url:
        print("❌ No URL provided")
        sys.exit(1)

    if not os.path.exists(cookies_path):
        print(f"❌ Cookies file not found: {cookies_path}")
        sys.exit(1)

    print(f"📥 Downloading: {url}")

    cmd = [
        "yt-dlp",
        "-v",
        "--cookies", cookies_path,
        "-o", "video.%(ext)s",
        url
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("❌ Download failed")
        sys.exit(1)

    # اتأكد إن الفيديو اتنزل
    files = glob.glob("video.*")
    if not files:
        print("❌ No video file found after download")
        sys.exit(1)

    video_file = files[0]
    size_mb = os.path.getsize(video_file) / (1024 * 1024)
    print(f"✅ Downloaded: {video_file} ({size_mb:.1f} MB)")

    # اكتب اسم الفايل في env عشان الـ workflow يعرفه
    with open(os.environ.get("GITHUB_ENV", "/dev/null"), "a") as f:
        f.write(f"VIDEO_FILE={video_file}\n")

    return video_file


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VIDEO_URL", "")
    download(url)
