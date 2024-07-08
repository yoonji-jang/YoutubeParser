import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

release = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
version = requests.get(release).text
# define environment
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")
chrome_options.add_argument("lang=ko")
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=chrome_options)
driver_video = webdriver.Chrome(options=chrome_options)
