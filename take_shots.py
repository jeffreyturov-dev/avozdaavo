#!/usr/bin/env python3
"""Take the 3 article screenshots via local Playwright chromium (mobile viewport)."""
import time
from playwright.sync_api import sync_playwright

URL = "https://tariff-ventures-income-insights.trycloudflare.com/"
OUT = "/opt/data/projet/avozdaavo/docs"
CHROME = "/opt/data/home/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 414, "height": 850},
                        device_scale_factor=2, is_mobile=True, has_touch=True,
                        locale="pt-PT")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)

    # 1. ask view with a real answer
    page.fill("#q", "Avó, como era a tua aldeia em Portugal?")
    page.evaluate("ask()")
    page.wait_for_selector("#answer:not(.hidden)", timeout=120000)
    time.sleep(1)
    page.screenshot(path=f"{OUT}/shot_ask.png")
    print("shot_ask OK")

    # 2. stories list
    page.evaluate("tab('list')")
    time.sleep(2)
    page.screenshot(path=f"{OUT}/shot_stories.png")
    print("shot_stories OK")

    # 3. record view
    page.evaluate("tab('record')")
    time.sleep(1)
    page.screenshot(path=f"{OUT}/shot_record.png")
    print("shot_record OK")

    b.close()
print("ALL SHOTS DONE")
