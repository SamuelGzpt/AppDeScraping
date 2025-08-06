from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Opcional: modo sin ventana

service = Service("C:/chromedriver/chromedriver-win64/chromedriver.exe")  # Ruta real
driver = webdriver.Chrome(service=service, options=options)

driver.get('https://www.google.com')
print(driver.title)
driver.quit()