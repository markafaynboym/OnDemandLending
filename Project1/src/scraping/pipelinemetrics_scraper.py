"""
Purpose: Scrapes the Pipeline Metrics tab and exports the CSV file.
Author: Mark Faynboym
Date: Oct-09-2025
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from selenium.webdriver.support.ui import Select

def scrape_pipeline_metrics(driver, wait, download_dir):
    time.sleep(1)
    print(1)
    # Click "Reporting" to expand submenu
    reporting_menu = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[contains(., 'Reporting')]"))
    )
    ActionChains(driver).move_to_element(reporting_menu).click().perform()
    print("✅ 'Reporting' menu clicked")
    time.sleep(1)

    # Wait for spinner to disappear
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    time.sleep(1)

    # Click "Pipeline Metrics"
    pipeline_metrics_link = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//a[@href='/admin/pipeline-metrics' and contains(., 'Pipeline Metrics')]"))
    )
    pipeline_metrics_link.click()
    print("✅ 'Pipeline Metrics' clicked")

    # Wait for page to load
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    time.sleep(2)

    # Click the outer "This Week" filter button
    outer_filter_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[contains(text(), 'This Week')]]"))
    )
    outer_filter_button.click()
    print("✅ Outer 'This Week' filter clicked")
    time.sleep(1)

    # Wait for popover to appear
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[contains(@class, 'popover')]"))
    )
    time.sleep(0.5)

    # Click the inner "This Week" dropdown
    inner_dropdown = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@id='dropdownBasic1' and .//span[contains(text(), 'This Week')]]"))
    )
    inner_dropdown.click()
    print("✅ Inner 'This Week' dropdown clicked")
    time.sleep(0.5)

    # Select "Custom" from dropdown
    custom_option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[contains(@class, 'dropdown-menu')]//button[.//span[contains(text(), 'Custom')]]"))
    )
    custom_option.click()
    print("✅ 'Custom' date range selected")

    # Wait for spinner to disappear and layout to settle
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ngx-spinner-overlay")))
    time.sleep(1)

    # Set 'From' date to 03/28/2024
    from_input = wait.until(EC.element_to_be_clickable((By.ID, "beginDate")))
    driver.execute_script("arguments[0].scrollIntoView(true);", from_input)
    from_input.click()
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, from_input, "2023-01-01")
    print("📅 'From' date set to 01/01/2023 MM/DD/YYYY")
    time.sleep(2)
    driver.find_element(By.TAG_NAME, "body").click()
    time.sleep(2)  # Let layout settle

    time.sleep(1)
    # Re-fetch the dropdown inside Pipeline Metrics section
    dropdown = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h4[.//span[text()='Pipeline Metrics']]//select"))
    )
    select = Select(dropdown)

    # Log all options to confirm visibility
    for i, opt in enumerate(select.options):
        print(f"[{i}] {opt.text.strip()} → {opt.get_attribute('value')}")

    # Select by visible text (robust against value changes)
    select.select_by_visible_text("Lead Ref ID")
    print("✅ 'Lead Ref ID' selected by visible text")
    time.sleep(1)

    # Step: Wait for the first accordion button to be clickable
    accordion_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//button[contains(@class, 'accordion-button')])[1]"))
    )
    accordion_button.click()
    print("📂 First accordion clicked")
    time.sleep(1)


    #  Click the columns dropdown trigger
    columns_trigger = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//p-multiselect//div[contains(@class, 'p-multiselect-trigger')]"))
    )
    columns_trigger.click()
    print("🧩 Columns dropdown opened")
    time.sleep(1)

    #  Wait for the checkbox overlay to appear
    checkbox_panel = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[contains(@class, 'p-overlay') and contains(@class, 'p-component')]"))
    )
    time.sleep(0.5)

    # Click the first checkbox (usually 'Select All')
    first_checkbox = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "(//div[contains(@class, 'p-overlay')]//div[contains(@class, 'p-checkbox')])[1]"))
    )
    first_checkbox.click()
    print("✅ First checkbox clicked (Select All)")
    time.sleep(3)

    # Trigger CSV export
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Export To CSV')]"))).click()
    time.sleep(2)

    # Rename the most recent download
    files = sorted(os.listdir(download_dir), key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
    latest_file = files[0]
    os.rename(os.path.join(download_dir, latest_file), os.path.join(download_dir, "PipelineMetrics_LOS.csv"))
    print("✅ PipelineMetrics_LOS.csv downloaded and renamed.")
