"""
Purpose: Automates scraping of LoanStatus data by selecting 'Pipeline', choosing a view, enabling all columns, and exporting.

Why: Mirrors the structure of pipeline_metrics scraper for consistency and modularity.
Author: Mark Faynboym
Date: Oct-09-2025
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def scrape_loanstatus(driver, wait, download_dir):
    # Navigate to 'Pipeline' tab
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pipeline')]"))).click()
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))

    # Click 'All' loan statuses
    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='button0']"))).click()
    time.sleep(2)

    # Wait for all overlays to disappear
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

    # Click 'Select a View' dropdown
    wait.until(EC.element_to_be_clickable((By.ID, "dropdownBasic1"))).click()
    time.sleep(2)

    # Wait for both spinner overlays to disappear
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))
    time.sleep(1)

    # Open column selector dropdown
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'p-multiselect-label-container')]"))).click()
    time.sleep(1)

    # Click the first checkbox (Select All)
    wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@role='checkbox'])[1]")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@role='checkbox'])[1]"))).click()
    time.sleep(2)

    # Close dropdown by clicking outside
    driver.find_element(By.TAG_NAME, "body").click()
    time.sleep(2)

    # Wait for final spinner and table to render
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table')]//tbody/tr")))
    time.sleep(1)

    # Click 'Export To CSV'
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(text(), 'Export To CSV')]"))).click()
    time.sleep(1.5)

    # Rename the downloaded file
    files = sorted(os.listdir(download_dir), key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
    latest_file = files[0]
    os.rename(os.path.join(download_dir, latest_file), os.path.join(download_dir, "Loanstatus.csv"))
    print("✅ Loanstatus.csv downloaded and renamed.")
