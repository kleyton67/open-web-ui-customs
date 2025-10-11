
import re
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium.webdriver.remote.webelement import WebElement
from typing import List
from time import sleep
import string
from bs4 import BeautifulSoup
import asyncio
from queue import Queue


class CrawlerResponse(BaseModel):
    url: str
    content: str

def process_url(url: str, results_queue: Queue):
    result = crawler(url=url)
    if isinstance(result, Exception):
        results_queue.put((url, result))
    else:
        results_queue.put((url, result.content))

def crawler(url: str) -> CrawlerResponse:
    options = Options()
    options.add_argument("--headless")  # For headless testing
    options.assume_request_during_headless = True
    # options.binary_location = "/opt/waterfox/waterfox"
    options.binary_location = "/usr/bin/firefox"
    # driver_path = "/opt/geckodriver/geckodriver"
    driver_path = "/usr/src/app/geckodriver"

    # firefox_profile.set_preference(
    #     'intl.accept_languages', 'en-US'
    # )
    options.set_preference(
        'geo.enabled', True
    )
    options.set_preference('geo.provider.network.url',
    'data:application/json,{"location": {"lat": 51.47, "lng": 0.0}, "accuracy": 100.0}')
    # options.profile = firefox_profile

    service = Service(executable_path=driver_path)

    try:
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url)

        wait = WebDriverWait(driver, 10)
        # element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-js-loaded]')))
        # element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-ready]')))
        # element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-script-loaded]')))

        # html = element.get_attribute("innerHTML")
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except:
        driver.close()
        driver.quit()
        return CrawlerResponse(
            url=url,
            content="Non acessible"
        )
    finally:
        driver.close()
        driver.quit()

    # Remove unnecessary tags and attributes
    for script in soup(["script", "style"]):
        script.extract()  # Remove script and style elements

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

# Step 3: Ou
    translator = str.maketrans(string.whitespace,
        " " * len(string.whitespace),
    )
    cleaned_text = soup.get_text().translate(translator)

    cleaned_text = re.sub(r' +', ' ', cleaned_text)

    return CrawlerResponse(
        url=url,
        content=cleaned_text
    )

if __name__ == "__main__":
    data_ret = asyncio.run(crawler(url="https://www.climatempo.com.br/previsao-do-tempo/15-dias/cidade/802/mongagua-sp"))
    import pdb
    pdb.set_trace()