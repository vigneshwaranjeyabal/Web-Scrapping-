from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import pandas as pd
import os
 
# Path to your ChromeDriver
CHROMEDRIVER_PATH = "chromedriver.exe"
 
# Load environment variables
load_dotenv()
 
# LinkedIn credentials
USERNAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('LINKEDIN_PASSWORD')
 
# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")
 
# Initialize Chrome WebDriver
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
wait = WebDriverWait(driver, 30)
 
# Navigate to LinkedIn login page
driver.get("https://www.linkedin.com/login")
 
# Log in to LinkedIn
email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
email_input.send_keys(USERNAME)
password_input = driver.find_element(By.ID, "password")
password_input.send_keys(PASSWORD)
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()
 
# Wait for the page to load
time.sleep(1)
 
# Search for "hiring for #servicenow" on the home page
search_bar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input")))
search_bar.send_keys("hiring for #servicenow")
search_bar.send_keys(Keys.RETURN)
 
# Wait for the search results page to load
time.sleep(1)
 
# Click on the "Posts" tab to filter only posts
posts_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Posts']")))
posts_tab.click()
 
# Wait for the posts to load
time.sleep(1)
 
# Open the "Date Posted" filter dropdown
date_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Date posted']")))
date_filter.click()
 
# Wait for the dropdown to open
time.sleep(1)
 
# Select the "Past 24 hours" option
past_24_hours = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Past 24 hours']")))
past_24_hours.click()
 
# Wait for the filtered results to load
time.sleep(1)
 
# Click the "Show Results" button to apply the filter
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
show_results_button.click()
 
# Wait for the filtered results to load
time.sleep(1)
 
# Function to clean up HTML to plain text
def clean_html(html):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser").get_text(strip=True)
 
# Function to scrape posts until the last post is reached
def scrape_all_posts():
    post_data = []  # List to store post details
    last_height = driver.execute_script("return document.body.scrollHeight")  # Track the last scroll height
 
    while True:
        # Wait for post containers to be present on the page
        post_containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fie-impression-container")))
 
        # Loop through each post container on the page
        for post in post_containers:
            try:
                # Scroll to the post to ensure it's in view
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(2)  # Allow time for scroll and lazy-load elements
 
                # Extract author, description, and time posted
                author_span = post.find_element(By.CLASS_NAME, "update-components-actor__name").find_element(By.CSS_SELECTOR, "span[dir='ltr'] span[aria-hidden='true']")
                author = author_span.text
                time_posted_element = post.find_element(By.CLASS_NAME, "update-components-actor__sub-description")
                time_posted = time_posted_element.find_element(By.XPATH, ".//span[@aria-hidden='true']").text
 
                # Extract the description (with HTML stripped)
                description_element = post.find_element(By.CLASS_NAME, "update-components-text")
                description_html = description_element.get_attribute('innerHTML')
 
                # Clean up the HTML to get a readable text format
                description = clean_html(description_html)
 
                # Click the "More options" (three dots) button for the post
                more_options_button = post.find_element(By.XPATH, ".//button[contains(@aria-label,'Open control menu for post by')]")
                driver.execute_script("arguments[0].click();", more_options_button)
                time.sleep(2)  # Wait for the menu to open
 
                # Click on "Copy link to post" from the menu
                copy_link_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Copy link to post']")))
                copy_link_option.click()
                time.sleep(2)  # Allow time for the link to be copied
 
                # Retrieve the copied link from the clipboard
                post_link = driver.execute_script("return navigator.clipboard.readText()")
 
                # Append the post details to the list in the desired order
                post_data.append({
                    "Author": author,
                    "Description": description,
                    "Time Posted": time_posted,
                    "Post Link": post_link,
                })
 
                # Close the modal after copying the link
                close_modal_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                close_modal_button.click()
                time.sleep(2)
 
            except Exception as e:
                print(f"Error scraping post: {e}")
                continue
 
        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load
       
        # Check if more posts have been loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If the scroll height hasn't changed, we've reached the bottom of the page
            print("Reached the last post.")
            break
        last_height = new_height  # Update the last scroll height
 
    return post_data
 
# Scrape all available posts
all_post_data = scrape_all_posts()
 
# Convert the data to a pandas DataFrame
post_df = pd.DataFrame(all_post_data, columns=["Author", "Description", "Time Posted", "Post Link"])
 
# Function to get a unique filename (to prevent overwriting)
def get_unique_filename(base_name, extension):
    counter = 1
    filename = f"{base_name}.{extension}"
   
    while os.path.exists(filename):
        filename = f"{base_name}({counter}).{extension}"
        counter += 1
   
    return filename
 
# Get a unique filename for saving the data
excel_filename = get_unique_filename("sorted", "xlsx")
 
# Save the DataFrame to an Excel file
post_df.to_excel(excel_filename, index=False)
 
# Close the browser
driver.quit()
 
print(f"Scraping complete. Saved to {excel_filename}.")