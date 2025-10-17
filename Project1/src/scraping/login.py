"""
Purpose: Handles login flow and dismisses modals.

Why: Encapsulates authentication logic so it’s reusable across scraping tasks and easier to maintain if the login UI changes.
Authors: Mark Faynboym
Date: Oct-09-2025
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
from dotenv import load_dotenv

load_dotenv()

def login(driver, wait):
    email = os.getenv("SCRAPER_EMAIL")
    password = os.getenv("SCRAPER_PASSWORD")  # Not used yet, but ready for next step
    time.sleep(1)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # Navigate to login page
    driver.get("https://ondemand.lodasoft.com/login")
    print("🔗 Navigated to login page")
    time.sleep(1)
    # Wait for username field and enter email
    wait.until(EC.element_to_be_clickable((By.ID, "login-username"))).send_keys(email)
    time.sleep(1)

    # Step 3: Click first login button to advance
    wait.until(EC.element_to_be_clickable((By.ID, "login-login-btn2"))).click()
    print("➡️ Submitted username")

    wait.until(EC.element_to_be_clickable((By.ID, "login-password"))).send_keys(password)

    # Click login button
    wait.until(EC.element_to_be_clickable((By.ID, "login-login-btn1"))).click()
    print("🔐 Clicked login button")

    # Optional: wait for dashboard to load
    time.sleep(2)
    print("✅ Login attempt complete")

    #Get rid of notification
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Dismiss']"))).click()