from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
from dotenv import load_dotenv  # NEW: For loading .env file

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("GENIEBOOK_USERNAME")
PASSWORD = os.getenv("GENIEBOOK_PASSWORD")

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Login to Geniebook
driver.get("https://app.geniebook.com/")
time.sleep(3)

driver.find_element(By.NAME, "email").send_keys(USERNAME)
driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
time.sleep(5)

# Navigate to Completed/Expired Worksheets
driver.get("https://app.geniebook.com/mathematics/worksheets/completed")
time.sleep(5)

# Select only P5-P6 worksheets
worksheets = driver.find_elements(By.XPATH, "//div[contains(text(), 'P5') or contains(text(), 'P6')]")
worksheet_links = [ws.find_element(By.XPATH, "./ancestor::a").get_attribute("href") for ws in worksheets]

# Directory to save PDFs
download_dir = "./geniebook_pdfs"
os.makedirs(download_dir, exist_ok=True)

# Download PDFs
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(os.path.join(download_dir, filename), 'wb') as f:
            f.write(response.content)

# Process each worksheet
for link in worksheet_links:
    driver.get(link)
    time.sleep(3)
    
    # Click Print PDF button
    print_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Print PDF')]")
    print_button.click()
    time.sleep(5)
    
    # Switch to new tab and extract PDF URL
    driver.switch_to.window(driver.window_handles[-1])
    pdf_url = driver.current_url
    filename = pdf_url.split("/")[-1]
    
    # Download PDF
    download_pdf(pdf_url, filename)
    
    # Close the PDF tab and switch back
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Cleanup
driver.quit()
print("Download completed!")
