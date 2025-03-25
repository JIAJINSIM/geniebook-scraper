# Alternative approach using image-based automation (PyAutoGUI)

import pyautogui
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
USERNAME = os.getenv("GENIEBOOK_USERNAME")
PASSWORD = os.getenv("GENIEBOOK_PASSWORD")

# Open browser manually to ensure rendering is accurate
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get("https://app.geniebook.com/")
wait = WebDriverWait(driver, 30)

# Login manually
try:
    email_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")
    email_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD + Keys.RETURN)
    print("✅ Logged in successfully")
    time.sleep(10)
except Exception as e:
    print(f"❌ Login error: {e}")
    driver.quit()
    exit()

# Go to Worksheets Page
driver.get("https://app.geniebook.com/mathematics/worksheets")
time.sleep(8)

# Force focus to browser window
try:
    chrome_window = pyautogui.getWindowsWithTitle("Geniebook")[0]
    chrome_window.activate()
    time.sleep(1)
except:
    print("⚠️ Could not activate Chrome window (may still work)")

# Search for and click Completed tab
print("🖱️ Searching for 'Completed' tab using image match...")
try:
    completed_location = pyautogui.locateCenterOnScreen("completed_tab.png", confidence=0.4)
    if completed_location:
        pyautogui.moveTo(completed_location)
        pyautogui.click()
        print("✅ Clicked Completed tab")
        time.sleep(3)
    else:
        raise pyautogui.ImageNotFoundException("Completed tab not found")
except Exception as e:
    pyautogui.screenshot("debug_completed_not_found.png")
    print(f"❌ Could not find Completed tab. Screenshot saved. Reason: {e}")
    driver.quit()
    exit()

# Locate all visible More (3-dot) buttons initially
print("🔄 Locating all visible More buttons...")
more_buttons = list(pyautogui.locateAllOnScreen("more_button.png", confidence=0.5))
print(f"🔍 Found {len(more_buttons)} 3-dot buttons on screen.")

for i, btn in enumerate(more_buttons):
    center = pyautogui.center(btn)
    pyautogui.moveTo(center)
    pyautogui.click()
    print(f"🟢 Clicked More button #{i + 1} at {center}")
    time.sleep(1)

    # Improved wait and click for Print PDF
    print("🧾 Waiting for 'Print PDF' option to appear...")
    found_pdf = False
    for _ in range(8):
        pdf_option = pyautogui.locateCenterOnScreen("print_pdf.png", confidence=0.6)
        if pdf_option:
            pyautogui.moveTo(pdf_option, duration=0.3)
            pyautogui.click()
            found_pdf = True
            print("✅ Clicked 'Print PDF' successfully")
            break
        time.sleep(1)

    if not found_pdf:
        pyautogui.screenshot(f"debug_print_pdf_not_found_{int(time.time())}.png")
        print("❌ Print PDF not found. Screenshot saved.")
        continue

    # Wait for new tab to appear
    print("🕒 Waiting for new tab to render print page...")
    time.sleep(5)

    # Click on actual system 'Print' button to trigger save
    print("🖨️ Clicking actual browser print button...")
    print_btn = None
    for _ in range(6):
        print_btn = pyautogui.locateCenterOnScreen("chrome_print_button.png", confidence=0.7)
        if print_btn:
            pyautogui.moveTo(print_btn)
            pyautogui.click()
            print("💾 Triggered save from print button.")
            break
        time.sleep(1)

    if not print_btn:
        pyautogui.screenshot("debug_print_button_not_found.png")
        print("❌ Print button not found. Screenshot saved.")
        continue

    # Wait for Save As dialog and click filename input
    print("💬 Waiting for Save As dialog...")
    time.sleep(2)
    pyautogui.click(200, 700)  # Adjust this to center on your filename input box
    pyautogui.write(f"worksheet_{int(time.time())}.pdf")
    pyautogui.press("enter")
    print("✅ Saved file")

    # Wait and close the current worksheet view
    time.sleep(5)
    pyautogui.hotkey('ctrl', 'w')  # Close tab (same tab returns to worksheet list)
    print("🔙 Returned to worksheet list")
    time.sleep(3)

print("✅ All visible PDFs processed")
driver.quit()
