import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pyppeteer import launch
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    browser = await launch()
    app.state.browser = browser
    yield
    # Clean up the ML models and release the resources
    await app.state.browser.close()

app = FastAPI(lifespan=lifespan)

@app.get("/input")
async def input(url: str, selector: str,  input_text: str):
    print("requested to input text:", input_text, "into selector:", selector, "at url:", url)
    
    # Create a new page
    page = await app.state.browser.newPage()
    
    # Navigate to the URL
    await page.goto(url)

    await page.type(selector, input_text)

    fname = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".png"
    # Take a screenshot of the webpage
    await page.screenshot(path=fname, type="png")
    # Close the page
    await page.close()
    
    return {"success": "true"}

@app.get("/navigate")
async def navigate_to_url(url: str):
    # Create a new page
    page = await app.state.browser.newPage()
    
    # Navigate to the URL
    await page.goto(url)

    content = await page.content()
    print("got page content:", content)

    # Close the page
    await page.close()
    
    return {"content": content}

@app.get("/getLinks")
async def get_all_links(url: str):
    print("getting links at url:", url)
    # Create a new page
    page = await app.state.browser.newPage()
    
    # Navigate to the URL
    await page.goto(url)

    links = await page.querySelectorAll('a')
    hrefs = []
    for link in links:
        hrefs.append(await page.evaluate('(element) => element.href', link))

    # Close the page
    await page.close()
    
    return {"links": hrefs}

@app.get("/screenshot")
async def take_screenshot(url: str):
    print("requested to take screenshot of url:", url)

    # Create a new page
    page = await app.state.browser.newPage()
    # Navigate to the URL
    await page.goto(url)
    
    #TODO: construct filename from url and timestamp
    fname = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".png"
    # Take a screenshot of the webpage
    await page.screenshot(path=fname, type="png")
    
    # Close the page
    await page.close()
    
    return {"status": "Success"}