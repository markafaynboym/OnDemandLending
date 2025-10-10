"""
Purpose: Launches Chrome browser with download directory configured.
Author: Mark Faynboym
Date: Oct-09-2025
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver(download_dir):
    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

