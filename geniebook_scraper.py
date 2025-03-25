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

# Get all worksheet cards using Selenium and filter P5-P6
print("🔍 Detecting worksheet cards using Selenium...")
try:
    # Try more reliable locator for worksheet cards
    try:
        # Try finding cards using a unique attribute or tag
        worksheet_cards = driver.find_elements(By.XPATH, "//div[contains(text(), 'P5') or contains(text(), 'P6')]")
    
        if not worksheet_cards:
            print("⚠️ No P5/P6 worksheet cards found with fallback XPath. Trying full card block...")
            worksheet_cards = driver.find_elements(By.CLASS_NAME, "MuiGrid-root")

        print(f"📄 Found {len(worksheet_cards)} total cards before filtering")

        filtered_cards = []
        for card in worksheet_cards:
            text = card.text
            if "P5" in text or "P6" in text:
                filtered_cards.append(card)
    
        print(f"🎯 Found {len(filtered_cards)} P5/P6 worksheet cards")
    except Exception as e:
        print(f"❌ Error while detecting or processing worksheet cards: {e}")
        driver.quit()
        exit()

    print(f"📄 Found {len(worksheet_cards)} total cards")

    filtered_cards = []
    for card in worksheet_cards:
        text = card.text
        if "P5" in text or "P6" in text:
            filtered_cards.append(card)

    print(f"🎯 Found {len(filtered_cards)} P5/P6 worksheet cards")

    for i, card in enumerate(filtered_cards):
        driver.execute_script("arguments[0].scrollIntoView(true);", card)
        time.sleep(1)
        card.click()
        print(f"➡️ Opened worksheet #{i + 1}")
        time.sleep(4)

        # Locate and click the More (3-dot) button
        more_button = pyautogui.locateCenterOnScreen("more_button.png", confidence=0.5)
        if more_button:
            pyautogui.moveTo(more_button)
            pyautogui.click()
            time.sleep(1)
        else:
            pyautogui.screenshot(f"debug_more_button_not_found_{i}.png")
            print("❌ More button not found. Screenshot saved.")
            continue

        # Click on 'Print PDF'
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
        time.sleep(6)

        # Click the print button
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

        # Wait for Save As dialog
        print("💬 Waiting for Save As dialog...")
        time.sleep(2)
        pyautogui.click(200, 700)  # Adjust if needed
        pyautogui.write(f"worksheet_{int(time.time())}.pdf")
        pyautogui.press("enter")
        print("✅ Saved file")

        # Close print tab
        time.sleep(5)
        pyautogui.hotkey('ctrl', 'w')
        print("✅ Closed print tab")

        # Reactivate Geniebook main tab (if needed)
        try:
            chrome_window.activate()
            time.sleep(1)
        except:
            pass

except Exception as e:
    print(f"❌ Error while detecting or processing worksheet cards: {e}")

print("✅ All visible P5/P6 PDFs processed")
driver.quit()
