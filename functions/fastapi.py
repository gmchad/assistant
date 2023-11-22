import requests
import os 

TOOLSERVER_BASE_URL = "http://localhost:8001"

def callFastAPI(command : str, url: str) -> str:
    fullURL = os.path.join(TOOLSERVER_BASE_URL, command)
    print("FastAPI URL:", fullURL)
    print("target URL to fetch:", url)

    response = requests.get(
        fullURL,
        params={"url": url}
    )
    # return json text.
    return response.text 

def inputText(url: str, selector: str, input_text: str) -> str:
    fullURL = os.path.join(TOOLSERVER_BASE_URL, 'input')
    print("FastAPI URL:", fullURL)
    print("target URL to fetch:", url, "selector:", selector, "input_text:", input_text)

    response = requests.get(
        fullURL,
        params={"url": url, "selector": selector, "input_text": input_text}
    )
    # return json text.
    return response.text 

