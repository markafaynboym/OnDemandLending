"""
Purpose: Automates scraping of Leads data by navigating to 'My Lists', selecting 'Leads',
applying filters, enabling all columns, and exporting to CSV.

Why: Mirrors the structure of loanstatus_scraper for consistency and modularity.
Author: Mark Faynboym
Date: Oct-09-2025
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import time

def scrape_leads(driver, wait, download_dir):
    time.sleep(2)
    # Step 1: Navigate to "My Lists" > "Leads"
    my_lists = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//span[contains(text(), 'My Lists')]")
    ))
    time.sleep(2)   
    ActionChains(driver).move_to_element(my_lists).click().perform()
    print("📂 'My Lists' clicked")
    time.sleep(2)

    # Wait for the Leads link to appear
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/admin/leads')]")))
    time.sleep(0.5)
    
    leads_link = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[@href='/admin/leads']")
    ))
    leads_link.click()

    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))

    # Click on the body to dismiss any overlays or floating lists
    driver.find_element(By.TAG_NAME, "body").click()
    time.sleep(0.5)  # Let layout settle
    # Step 2: Enable Power User Mode
    power_user_checkbox = wait.until(EC.presence_of_element_located((By.ID, "editModeToggle")))
    driver.execute_script("arguments[0].scrollIntoView(true);", power_user_checkbox)
    if not power_user_checkbox.is_selected():
        power_user_checkbox.click()

    # Step 3: Open Date Filter → Today → Custom → Set Date
    time.sleep(1)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//generic-date-range-filter//button[.//span[normalize-space()='Today']]"))
    ).click()

    popover_today = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'popover')]//button[.//span[normalize-space()='Today']]"))
    )
    popover_today.click()

    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'popover')]//button[.//span[normalize-space()='Custom']]"))
    ).click()

    time.sleep(1)
    from_input = wait.until(EC.element_to_be_clickable((By.ID, "beginDate")))
    driver.execute_script("arguments[0].scrollIntoView(true);", from_input)
    from_input.click()
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, from_input, "2024-03-28")
    time.sleep(2)
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    time.sleep(2)

    # Step 4: Open Column Selector → Select All
    dropdown_toggle = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.p-multiselect-trigger"))
    )
    dropdown_toggle.click()
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "div.p-multiselect-panel"))
    )
    select_all = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//div[contains(@class, 'p-multiselect-panel')]//div[@role='checkbox'])[1]"))
    )
    select_all.click()

    # Step 5: Export to CSV
    export_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[normalize-space()='Export To CSV']")
    ))
    export_button.click()
    time.sleep(2)
    # Step 6: Rename the downloaded file
    files = sorted(os.listdir(download_dir), key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
    latest_file = files[0]
    os.rename(os.path.join(download_dir, latest_file), os.path.join(download_dir, "Leads_CRM.csv"))
    print("✅ Leads.csv downloaded and renamed.")
