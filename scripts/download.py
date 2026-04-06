import yt_dlp

def run():
    url = "https://www.youtube.com/watch?v=R9VI4dyK9V4"
    
    ydl_opts = {
        'format': 'best',
        # تأكد إن ملف الكوكيز موجود في نفس مجلد scripts أو في الرئيسي
        # إذا كان في مجلد scripts، اكتب المسار هكذا:
        'cookiefile': 'scripts/cookies.txt', 
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    run()
