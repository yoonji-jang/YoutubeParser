from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# define environment
webdriver_options = wd.ChromeOptions()
webdriver_options.add_argument("headless")
webdriver_options.add_argument("lang=ko")
driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options)
driver_video = wd.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options)
