from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
 
 
# Path to your ChromeDriver
CHROMEDRIVER_PATH = "chromedriver.exe"

# LinkedIn credentials
USERNAME = "mathupugal21@gmail.com"
PASSWORD = "happyhome21"

# Configure Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Optional: Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")

# Initialize Chrome WebDriver
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

# Navigate to LinkedIn login page
driver.get("https://www.linkedin.com/login")

# Log in to LinkedIn
email_input = driver.find_element(By.ID, "username")
email_input.send_keys(USERNAME)
password_input = driver.find_element(By.ID, "password")
password_input.send_keys(PASSWORD)
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()

# Wait for the page to load
time.sleep(2)
 
driver.get("https://www.linkedin.com/jobs/")
time.sleep(2)

# Find the job search bar and enter your keywords (e.g., "Software Engineer")
search_bar = driver.find_element(By.CSS_SELECTOR, "input.jobs-search-box__text-input")
search_bar.send_keys("Software Engineer")
search_bar.send_keys(Keys.RETURN)
time.sleep(2)

# Function to scrape job listings
def scrape_jobs_on_page():
    job_titles = []
    # Find the <ul> container with class 'scaffold-layout__list-container'
    ul_container = driver.find_element(By.CLASS_NAME, "scaffold-layout__list-container")
    # Find all <li> elements inside the <ul> container
    li_elements = ul_container.find_elements(By.TAG_NAME, "li")
    # Loop through each <li> element and extract the job title
    for li in li_elements:
        try:
            # Find the <strong> element containing the job title
            job_title = li.find_element(By.TAG_NAME, "strong").text
            # Find the <li> element with class 'job-card-container__metadata-item' containing the job location
            job_location = li.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text

            company_name = li.find_element(By.CLASS_NAME, 'job-card-container__primary-description ').text
            # Append the job title and location as a dictionary to the jobs list
            job_titles.append({"Job Title": job_title, "Location": job_location, "Company_Name":company_name})
        except:
            # If no job title is found, continue to the next <li>
            continue
    return job_titles

# Initialize an empty list to store job details across pages
all_job_data = []
# Loop through pages to gather data (change 10 to the number of pages you want)
for page in range(1, 2):  # 10 pages
    print(f"Scraping page {page}...")
    jobs_on_page = scrape_jobs_on_page()
    all_job_data.extend(jobs_on_page)
    # Try to go to the next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
        next_button.click()
        time.sleep(2)  # Wait for the next page to load
    except:
        print("No more pages or next button not found")
        break
    
# Convert the job data into a pandas DataFrame
job_df = pd.DataFrame(all_job_data)

# Save the job data to an Excel file
job_df.to_excel("job.xlsx", index=False)
# Close the browser

driver.quit()
print("Scraping complete.")