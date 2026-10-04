#!/usr/bin/env python3
"""Regenerate all article visuals: grounded answer, honest refusal, stories, record, GIF."""
import time
from playwright.sync_api import sync_playwright

URL = "https://tariff-ventures-income-insights.trycloudflare.com/"
OUT = "/opt/data/projet/avozdaavo/docs"
CHROME = "/opt/data/home/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage"])

    # --- stills ---
    ctx = b.new_context(viewport={"width": 414, "height": 850},
                        device_scale_factor=2, is_mobile=True, has_touch=True,
                        locale="pt-PT")
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)

    page.fill("#q", "Pai, como é que nós viemos para o Luxemburgo?")
    page.evaluate("ask()")
    page.wait_for_selector("#answer:not(.hidden)", timeout=180000)
    time.sleep(1)
    page.screenshot(path=f"{OUT}/shot_ask.png")
    print("shot_ask OK")

    # honest refusal shot
    page.fill("#q", "Pai, qual era o teu prato preferido quando eras pequeno?")
    page.evaluate("ask()")
    time.sleep(8)
    page.wait_for_selector("#answer:not(.hidden)", timeout=60000)
    time.sleep(1)
    page.screenshot(path=f"{OUT}/shot_honest.png")
    print("shot_honest OK")

    page.evaluate("tab('list')")
    time.sleep(2)
    page.screenshot(path=f"{OUT}/shot_stories.png")
    print("shot_stories OK")

    page.evaluate("tab('record')")
    time.sleep(1)
    page.screenshot(path=f"{OUT}/shot_record.png")
    print("shot_record OK")
    ctx.close()

    # --- GIF ---
    ctx = b.new_context(viewport={"width": 414, "height": 850},
                        device_scale_factor=2, is_mobile=True, has_touch=True,
                        record_video_dir=OUT, record_video_size={"width": 414, "height": 850})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)
    page.fill("#q", "Quantos anos tinhas quando vieste para o Luxemburgo?")
    time.sleep(1)
    page.evaluate("ask()")
    page.wait_for_selector("#answer:not(.hidden)", timeout=180000)
    time.sleep(3)
    page.evaluate("tab('list')")
    time.sleep(2.5)
    page.evaluate("tab('record')")
    time.sleep(2)
    ctx.close()
    b.close()
print("ALL VISUALS DONE")
