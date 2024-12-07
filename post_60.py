from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
 
# Path to your ChromeDriver
CHROMEDRIVER_PATH = "chromedriver.exe"
 
# LinkedIn credentials
USERNAME = "mathupugal21@gmail.com"
PASSWORD = "happyhome21"
 
 
# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1200")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")
 
# Initialize Chrome WebDriver
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
wait = WebDriverWait(driver, 30)  # Set an explicit wait time of 15 seconds
 
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
# Update the XPATH to target the button more precisely
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
#driver.execute_script("arguments[0].scrollIntoView(true);", show_results_button)
#driver.execute_script("arguments[0].click();", show_results_button)
 
 
# Wait for the filtered results to load
time.sleep(2)
show_results_button.click()
 
# Wait for the filtered results to load
time.sleep(2)
# Function to scrape posts on the current page and fetch the post link and other details
def scrape_posts(max_posts=60):
    post_data = []  # List to store post details
    posts_scraped = 0  # Counter for scraped posts
    scroll_attempts = 0  # Count of scroll attempts in case we need more posts

    while posts_scraped < max_posts and scroll_attempts < 70:
        # Wait for post containers to be present on the page
        post_containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fie-impression-container")))
        
        # Loop through each post container in order
        for post in post_containers[posts_scraped:]:
            if posts_scraped >= max_posts:
                break  # Stop when we have collected the required number of posts
            
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

                # Retrieve the copied link from the clipboard (You may need to adapt this part based on clipboard access)
                post_link = driver.execute_script("return navigator.clipboard.readText()")

                # Append the post details to the list in the desired order
                post_data.append({
                    "Author": author,
                    "Description": description,
                    "Time Posted": time_posted,
                    "Post Link": post_link
                })
                posts_scraped += 1  # Increment the counter

                # Close the modal after copying the link
                close_modal_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                close_modal_button.click()
                time.sleep(2)

            except Exception as e:
                print(f"Error scraping post: {e}")
                continue
        
        # Scroll down if fewer than 10 posts have been scraped
        if posts_scraped < max_posts:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for new content to load
            scroll_attempts += 1

    return post_data

# Scrape the first 10 posts in order
all_post_data = scrape_posts(max_posts=60)

# Convert the data to a pandas DataFrame and save it to an Excel file
post_df = pd.DataFrame(all_post_data, columns=["Author", "Description", "Time Posted", "Post Link"])
post_df.to_excel("post_60.xlsx", index=False)

# Close the browser
driver.quit()

print("Scraping complete.")
