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
import re

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
time.sleep(2)

# Search for "ServiceNow" on the home page
search_bar = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input")))
search_bar.send_keys("hiring for #servicenow")
search_bar.send_keys(Keys.RETURN)

# Wait for the search results page to load
time.sleep(2)

# Click on the "Posts" tab to filter only posts
posts_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Posts']")))
posts_tab.click()

# Wait for the posts to load
time.sleep(2)

# Open the "Date Posted" filter dropdown
date_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Date posted']")))
date_filter.click()

# Wait for the dropdown to open
time.sleep(2)

# Select the "Past 24 hours" option
past_24_hours = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Past 24 hours']")))
past_24_hours.click()

# Wait for the filtered results to load
time.sleep(2)

# Click the "Show Results" button to apply the filter
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
show_results_button.click()

# Wait for the filtered results to load
time.sleep(2)

# Function to scrape all posts until the last post is reached
def scrape_all_posts():
    post_data = []  # List to store post details
    posts_scraped = 0  # Counter for scraped posts
    last_height = driver.execute_script("return document.body.scrollHeight")  # Track the last scroll height

    while True:
        # Wait for post containers to be present on the page
        post_containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fie-impression-container")))

        # Loop through each post container on the page
        for post in post_containers[posts_scraped:]:
            try:
                # Scroll to the post to ensure it's in view
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(2)  # Allow time for scroll and lazy-load elements

                # Extract author, description, and time posted
                author = post.find_element(By.CLASS_NAME, "update-components-actor__name").text
                description = post.find_element(By.CLASS_NAME, "break-words").text
                time_posted_element = post.find_element(By.CLASS_NAME, "update-components-actor__sub-description")
                time_posted = time_posted_element.find_element(By.XPATH, ".//span[@aria-hidden='true']").text

                # Click the "More options" (three dots) button for the post
                more_options_button = post.find_element(By.XPATH, ".//button[contains(@aria-label,'Open control menu for post by')]")
                driver.execute_script("arguments[0].click();", more_options_button)
                time.sleep(2)  # Wait for the menu to open

                # Click on "Copy link to post" from the menu
                copy_link_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Copy link to post']")))
                copy_link_option.click()
                time.sleep(2)  # Allow time for the link to be copied

                # Retrieve the copied link from the clipboard (adapt as needed for clipboard access)
                post_link = driver.execute_script("return navigator.clipboard.readText()")

                # Append the post details to the list
                post_data.append({
                    "Author": author,
                    "Description": description,
                    "Time Posted": time_posted,
                    "Post Link": post_link,
                })
                posts_scraped += 1  # Increment the counter

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

# Function to convert time posted (like '5m', '3h') into minutes
def convert_to_minutes(time_posted):
    # Remove unnecessary parts like '• Edited •'
    time_posted = re.sub(r'•.*$', '', time_posted).strip()

    # Extract the number and unit (m for minutes, h for hours)
    match = re.match(r"(\d+)([mh])", time_posted)
    if match:
        value, unit = match.groups()
        value = int(value)
       
        if unit == 'm':  # If the time is in minutes, return as is
            return value
        elif unit == 'h':  # If the time is in hours, convert to minutes
            return value * 60
    return float('inf')  # If no match, return infinity to push it to the end of the sort

# Apply the function to the 'Time Posted' column
post_df['Time Posted (Minutes)'] = post_df['Time Posted'].apply(convert_to_minutes)

# Sort the DataFrame by 'Time Posted (Minutes)' column in ascending order
sorted_post_df = post_df.sort_values(by='Time Posted (Minutes)', ascending=True)

# Drop the helper column if you don't need it anymore
sorted_post_df = sorted_post_df.drop(columns=['Time Posted (Minutes)'])

# Save the sorted DataFrame to an Excel file
sorted_post_df.to_excel("infinite_sort.xlsx", index=False)

# Close the browser
driver.quit()

print("Scraping and sorting complete.")
