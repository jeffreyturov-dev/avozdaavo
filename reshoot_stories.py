#!/usr/bin/env python3
"""Regenerate the stories-list screenshot (now 2 stories)."""
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
    page.evaluate("tab('list')")
    time.sleep(2)
    page.screenshot(path=f"{OUT}/shot_stories.png")
    print("shot_stories regenerated")
    b.close()
