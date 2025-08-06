from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
service = Service("C:/chromedriver/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(options=options, service=service)
driver.get("https://www.fcm.org.co/simit/#/home-public")
print(driver.title)
driver.quit()