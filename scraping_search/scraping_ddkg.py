
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
from loguru import logger


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

class Searcher:
    def __init__(self):
        # Set up options
        options = Options()
        options.add_argument("-headless")  # For headless testing
        options.assume_request_during_headless = True
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.binary_location = "/usr/bin/firefox"
        # service = Service(executable_path="/usr/src/app/geckodriver")
        options.binary_location = "/opt/waterfox/waterfox"
        service = Service(executable_path="/opt/geckodriver/geckodriver")
        
        # Initialize the driver
        self.driver = webdriver.Firefox(service=service, options=options)
    
    def ddkg_search(self, url: str, results_amount: int) -> List[SearchResult]:
        results_list: List[SearchResult] = []
        try:
            
            wait = WebDriverWait(self.driver, 5)

            kv=1

            while True:
                logger.info(f"Page: {kv}")
                self.driver.get(url+f"&kv={kv}")

                element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "react-results--main")))

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                list_items: List[WebElement] = element.find_elements(By.CSS_SELECTOR, 'li[data-layout="organic"]')
                
                for i, item in enumerate(list_items):
                    sleep(0.01)
                    if i >= results_amount:
                        break
                    results_list.append(
                        SearchResult(
                            title=item.find_element(By.CSS_SELECTOR, 'h2 a').text,
                            link=item.find_elements(By.CSS_SELECTOR, 'h2 a')[0].get_attribute("href"),
                            snippet=item.find_elements(By.CSS_SELECTOR, 'div [data-result="snippet"]')[0].text
                        )
                    )
                
                # TODO remover elementos iguais, da lista
                if len(results_list) >= results_amount:
                    break
                    
                kv+=1


            return results_list[:results_amount]
        
        except Exception as e:
            results_list.append(SearchResult(
                title="Error on server to get results",
                link="Error",
                snippet=str(e)
            ))
        
        return results_list
    
    def __del__(self):
        # Close and quit the driver
        self.driver.close()
        self.driver.quit()

if __name__ == "__main__":
    # Example usage
    search_obj = Searcher()
    l_results = search_obj.ddkg_search("https://duckduckgo.com/?q=test_123", 15)

    import pdb
    pdb.set_trace()