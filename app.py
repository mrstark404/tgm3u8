from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from playwright.async_api import async_playwright
import asyncio
import re

app = FastAPI()

async def get_m3u8(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto(url, timeout=15000)
        content = await page.content()

        # Search for m3u8 links in HTML
        m3u8_links = re.findall(r'https?://[^\s\'"]+\.m3u8', content)
        await browser.close()
        if not m3u8_links:
            return None
        return m3u8_links[0]

@app.get("/fetch")
async def fetch_m3u8(url: str):
    link = await get_m3u8(url)
    if not link:
        raise HTTPException(status_code=404, detail="No m3u8 link found")
    return RedirectResponse(link)
