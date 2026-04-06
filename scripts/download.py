import yt_dlp
import os
import sys

def run():
    # استلام البيانات من GitHub Actions
    url = os.environ.get("VIDEO_URL")
    cookies_content = os.environ.get("COOKIES_DATA")
    
    if not url:
        print("❌ Error: No URL provided!")
        sys.exit(1)

    # إنشاء ملف كوكيز مؤقت إذا تم إرساله من n8n
    cookie_file = 'scripts/temp_cookies.txt'
    if cookies_content and len(cookies_content) > 10:
        with open(cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookies_content)
        print("✅ Using cookies provided by n8n")
    else:
        # إذا لم يتم إرسال كوكيز، استخدم الملف الموجود في المستودع
        cookie_file = 'scripts/cookies.txt'
        print("ℹ️ Using local cookies.txt file")

    ydl_opts = {
        'format': 'best',
        'cookiefile': cookie_file,
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"📥 Starting download for: {url}")
            ydl.download([url])
            print("✅ Download Completed Successfully!")
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()
