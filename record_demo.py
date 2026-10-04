#!/usr/bin/env python3
"""Record a demo video of the ask flow via Playwright, for the article GIF."""
import time, os
from playwright.sync_api import sync_playwright

URL = "https://tariff-ventures-income-insights.trycloudflare.com/"
OUT = "/opt/data/projet/avozdaavo/docs"
CHROME = "/opt/data/home/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 414, "height": 850},
                        device_scale_factor=2, is_mobile=True, has_touch=True,
                        record_video_dir=OUT, record_video_size={"width": 414, "height": 850})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)
    page.fill("#q", "Avó, como era a tua aldeia em Portugal?")
    time.sleep(1)
    page.evaluate("ask()")
    page.wait_for_selector("#answer:not(.hidden)", timeout=120000)
    time.sleep(3)  # let viewers read
    page.evaluate("tab('list')")
    time.sleep(2.5)
    page.evaluate("tab('record')")
    time.sleep(2)
    ctx.close()  # finalizes video
    b.close()

vids = [f for f in os.listdir(OUT) if f.endswith(".webm")]
print("videos:", vids)
