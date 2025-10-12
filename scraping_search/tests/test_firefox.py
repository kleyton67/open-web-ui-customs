from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from pydantic import BaseModel
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--headless")  # For headless testing
options.assume_request_during_headless = True
# options.binary_location = "/opt/waterfox/waterfox"
options.binary_location = "/usr/bin/firefox"
# driver_path = "/opt/geckodriver/geckodriver"
driver_path = "/usr/src/app/geckodriver"

options.set_preference(
'geo.enabled', True
)
options.set_preference('geo.provider.network.url',
'data:application/json,{"location": {"lat": 51.47, "lng": 0.0}, "accuracy": 100.0}')
# options.profile = firefox_profile

service = Service(executable_path=driver_path)

driver = webdriver.Firefox(service=service, options=options)

driver.get("https://duckduckgo.com/")

soup = BeautifulSoup(driver.page_source, "html.parser")

print(soup)

driver.quit()