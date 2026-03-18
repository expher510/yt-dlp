import asyncio
import os
import sys


async def extract():
    from playwright.async_api import async_playwright

    email = os.environ.get("YT_EMAIL")
    password = os.environ.get("YT_PASSWORD")

    if not email or not password:
        print("❌ YT_EMAIL or YT_PASSWORD not set")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        )
        page = await context.new_page()

        print("🔄 Going to Google sign in...")
        await page.goto("https://accounts.google.com/signin", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # الخطوة 1: إيميل
        print("📧 Filling email...")
        await page.wait_for_selector('input[type="email"]', timeout=15000)
        await page.fill('input[type="email"]', email)
        await page.keyboard.press("Enter")

        # استنى صفحة الباسورد
        print("⏳ Waiting for password field...")
        await page.wait_for_selector('input[type="password"]', timeout=15000)
        await page.wait_for_timeout(1500)

        # الخطوة 2: باسورد
        print("🔑 Filling password...")
        await page.fill('input[type="password"]', password)
        await page.keyboard.press("Enter")

        # استنى يدخل
        print("⏳ Waiting for login...")
        await page.wait_for_timeout(5000)

        # تأكد إنه دخل
        current_url = page.url
        print(f"📍 Current URL: {current_url}")

        if "accounts.google.com" in current_url:
            # ممكن في 2FA أو verification
            print("⚠️ Still on Google accounts page - possible 2FA or verification needed")
            await page.screenshot(path="login_state.png")
            await browser.close()
            sys.exit(1)

        # روح على YouTube
        print("🎬 Going to YouTube...")
        await page.goto("https://www.youtube.com", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # روح على robots.txt عشان تحدث الـ cookies
        print("🤖 Going to robots.txt...")
        await page.goto("https://www.youtube.com/robots.txt")
        await page.wait_for_timeout(2000)

        # استخرج الـ cookies
        cookies = await context.cookies([
            "https://youtube.com",
            "https://www.youtube.com",
            "https://google.com",
            "https://www.google.com"
        ])

        print(f"🍪 Found {len(cookies)} cookies")

        # حول لـ Netscape format
        lines = ["# Netscape HTTP Cookie File\n"]
        for c in cookies:
            domain = c['domain']
            include_subdomain = "TRUE" if domain.startswith('.') else "FALSE"
            secure = "TRUE" if c.get('secure') else "FALSE"
            expires = int(c.get('expires', 0))
            if expires < 0:
                expires = 0

            lines.append(
                f"{domain}\t"
                f"{include_subdomain}\t"
                f"{c['path']}\t"
                f"{secure}\t"
                f"{expires}\t"
                f"{c['name']}\t"
                f"{c['value']}\n"
            )

        with open("cookies.txt", "w") as f:
            f.writelines(lines)

        await browser.close()
        print(f"✅ Cookies saved to cookies.txt ({len(cookies)} cookies)")


asyncio.run(extract())
