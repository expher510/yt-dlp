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

        # ── الخطوة 1: روح على صفحة اللوجين ──────────────
        print("🔄 Going to Google sign in...")
        await page.goto("https://accounts.google.com/signin", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # ── الخطوة 2: إيميل ───────────────────────────────
        print("📧 Filling email...")
        await page.wait_for_selector('input[type="email"]', timeout=15000, state="visible")
        await page.fill('input[type="email"]', email)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        # ── الخطوة 3: باسورد ──────────────────────────────
        print("⏳ Waiting for password field...")

        # جرب أكتر من selector عشان Google بيغير الـ HTML
        password_selectors = [
            'input[jsname="YPqjbf"]',                           # الـ selector الرسمي
            'input[type="password"]:not([aria-hidden="true"])',  # مش hidden
            'input[name="Passwd"]',                              # اسم قديم
            'input[autocomplete="current-password"]',            # autocomplete
        ]

        password_field = None
        for selector in password_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000, state="visible")
                password_field = selector
                print(f"✅ Found password field: {selector}")
                break
            except Exception:
                print(f"⚠️ Selector not found: {selector}")
                continue

        if not password_field:
            print("❌ Could not find password field - taking screenshot for debug")
            await page.screenshot(path="debug_password.png")
            print(f"📍 Current URL: {page.url}")
            await browser.close()
            sys.exit(1)

        print("🔑 Filling password...")
        await page.fill(password_field, password)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)

        # ── تأكد إنه دخل ──────────────────────────────────
        current_url = page.url
        print(f"📍 Current URL after login: {current_url}")

        if "accounts.google.com" in current_url:
            print("⚠️ Still on Google - possible 2FA or wrong credentials")
            await page.screenshot(path="debug_login.png")
            await browser.close()
            sys.exit(1)

        # ── الخطوة 4: روح على YouTube ─────────────────────
        print("🎬 Going to YouTube...")
        await page.goto("https://www.youtube.com", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # ── الخطوة 5: robots.txt ──────────────────────────
        print("🤖 Going to robots.txt...")
        await page.goto("https://www.youtube.com/robots.txt")
        await page.wait_for_timeout(2000)

        # ── الخطوة 6: استخرج الـ cookies ──────────────────
        cookies = await context.cookies([
            "https://youtube.com",
            "https://www.youtube.com",
            "https://google.com",
            "https://www.google.com"
        ])

        print(f"🍪 Found {len(cookies)} cookies")

        if len(cookies) == 0:
            print("❌ No cookies found!")
            await browser.close()
            sys.exit(1)

        # ── الخطوة 7: حول لـ Netscape format ──────────────
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
        print(f"✅ Cookies saved! ({len(cookies)} cookies)")


asyncio.run(extract())
