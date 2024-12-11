from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

chrome_driver_path = "C:\\ruta\\a\\chromedriver.exe"  #windows
chrome_driver_path = "C:\\SeleniumDrivers\\chromedriver.exe"  #linux

# Configuración del navegador
options = Options()
options.add_argument('--headless')  # Opcional: Si no necesitas una ventana de navegador visible
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled') 
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36')  # Cambia el User-Agent

# options.binary_location = '/usr/bin/chromium-browser'

# Inicializar WebDriver
# driver = webdriver.Chrome(options=options)

#windows
# Inicializar WebDriver
# service = Service(chrome_driver_path)
driver = webdriver.Chrome(options=options)
