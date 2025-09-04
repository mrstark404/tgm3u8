from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

async def get_m3u8(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=15000)
            
            # Search for m3u8 links in the page
            content = await page.content()
            m3u8_links = [line.split('"')[0] for line in content.split() if ".m3u8" in line]
            
            await browser.close()
            if m3u8_links:
                return m3u8_links[0]
            else:
                raise HTTPException(status_code=404, detail="No m3u8 found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fetch")
async def fetch_m3u8(url: str = Query(..., description="URL to fetch m3u8 from")):
    m3u8_link = await get_m3u8(url)
    return RedirectResponse(url=m3u8_link)
