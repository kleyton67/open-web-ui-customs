
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


class SearchResult(BaseModel):
    title: str
    link: str
    description: str

def ddkg_search(url: int, results_amount: int):
    # Set up options
    options = Options()
    options.add_argument("-headless")  # For headless testing
    options.assume_request_during_headless = True
    # options.binary_location = "/opt/waterfox/waterfox"
    options.binary_location = "librewolf"
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

    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "react-results--main")))

    list_items : List[WebElement] =  element.find_elements(By.CSS_SELECTOR, 'li[data-layout="organic"]')

    results_list = []
    for i, item in enumerate(list_items):
        #item.get_attribute("innerHTML") to see all html of this component
        sleep(0.01)
        if i > results_amount:
            break
        results_list.append(
            
            SearchResult(
                title=item.find_element(By.CSS_SELECTOR, 'h2 a').text,
                link=item.find_elements(By.CSS_SELECTOR, 'h2 a')[0].get_attribute("href"),
                description=item.find_elements(By.CSS_SELECTOR, 'div [data-result="snippet"]')[0].text
            )
        )
    
    driver.quit()
        
    return results_list[:results_amount]

if __name__ == "__main__":
    # Example usage
    l_results = ddkg_search("https://duckduckgo.com/?q=test_123", 5)

    import pdb
    pdb.set_trace()