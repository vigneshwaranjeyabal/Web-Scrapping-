from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import pandas as pd
import re
import os
from bs4 import BeautifulSoup
 
# Path to your ChromeDriver
CHROMEDRIVER_PATH = "chromedriver.exe"
 
load_dotenv()
 
# LinkedIn credentials
USERNAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('LINKEDIN_PASSWORD')
 
# Configure Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")
 
# Initialize Chrome WebDriver
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
wait = WebDriverWait(driver, 30)  # Set an explicit wait time of 30 seconds
 
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
 
# Wait for the posts to load
time.sleep(2)
 
# Click the "Show Results" button to apply the filter
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
show_results_button.click()
 
# Wait for the filtered results to load
time.sleep(2)
 
# Function to scrape posts on the current page and fetch the post link
def scrape_posts():
    post_data = []  # List to store post details
    previous_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0  # Keeps track of how many times the page was scrolled without finding new posts
 
    while True:
        # Wait for post containers to be present on the page
        post_containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fie-impression-container")))
 
        for post in post_containers[len(post_data):]:  # Process only new posts
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
 
                # Format the description to match your required output
                formatted_description = format_description(description)
 
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
 
        # Scroll down the page to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load
 
        # Check if the page height has changed (i.e., more posts have loaded)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            # No more new posts are being loaded, so exit the loop
            scroll_attempts += 1
            if scroll_attempts >= 2:  # If no new posts after 2 scroll attempts, break
                break
        else:
            previous_height = new_height
            scroll_attempts = 0  # Reset scroll attempts if new content is found
 
    return post_data
 
def clean_html(raw_html):
    # Create a BeautifulSoup object and extract text
    soup = BeautifulSoup(raw_html, "html.parser")
 
    # Remove the hidden "hashtag" span
    for hidden_text in soup.find_all("span", class_="visually-hidden"):
        if hidden_text.string == "hashtag":
            hidden_text.decompose()  # Remove the hidden span from the HTML
 
    # Get the clean text without "hashtag" and return it
    return ' '.join(soup.get_text(separator=' ', strip=True).split())
 
def format_description(description):
    # Split into words and filter out any unwanted characters
    words = description.split()  # Split into words
    hashtags = set()  # Use a set to avoid duplicates
 
    # Collect hashtags without leading '#'
    for word in words:
        if word.startswith("#") and word.strip("#"):
            hashtags.add(word.strip())  # Add only valid hashtags
 
    # Create formatted description
    formatted_desc = ' '.join(words)  # Original description
    # Join hashtags without duplicates and without leading/trailing spaces
    formatted_desc += ' ' + ' '.join(f"#{tag}" for tag in hashtags if tag)
    return ' '.join(formatted_desc.split()).strip()  # Return trimmed string
 
# Scrape the posts
all_post_data = scrape_posts()
 
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
 
# Sort the DataFrame by 'Time Posted (Minutes)'
sorted_df = post_df.sort_values(by="Time Posted (Minutes)").reset_index(drop=True)
 
# Remove the 'Time Posted (Minutes)' column
sorted_df.drop(columns=["Time Posted (Minutes)"], inplace=True)
 
# Function to generate a new file name if one already exists
def get_new_filename(base_name="file", ext=".xlsx"):
    # Start with base filename
    file_name = f"{base_name}{ext}"
    i = 1  # Start with 1 for naming like file(1).xlsx
   
    # Check if the file exists, and keep increasing the number if it does
    while os.path.exists(file_name):
        file_name = f"{base_name}({i}){ext}"
        i += 1
       
    return file_name
 
# Get a new file name
new_file_name = get_new_filename()
 
# Save the DataFrame to an Excel file with the new name
sorted_df.to_excel(new_file_name, index=False)
 
# Close the browser
driver.quit()
 
print(f"Data saved to {new_file_name}")