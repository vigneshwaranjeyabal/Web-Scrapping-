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
USERNAME = "vigneshwaranjeyabal@gmail.com"
PASSWORD = "Vignesh@1"
# Configure Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Optional: Run in headless mode
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
time.sleep(5)
 
# Click on the "Posts" tab to filter only posts
posts_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Posts']")))
posts_tab.click()
 
# Wait for the posts to load
time.sleep(5)
 
# Open the "Date Posted" filter dropdown
date_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Date posted']")))
date_filter.click()
 
# Wait for the dropdown to open
time.sleep(5)
 
# Select the "Past 24 hours" option
past_24_hours = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Past 24 hours']")))
past_24_hours.click()
 
# Wait for the posts to load
time.sleep(5)
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
show_results_button.click()
 
time.sleep(5)
 
# Function to scrape posts
# Function to scrape posts
def scrape_post_content(post_element):
    try:
        # Check if "View Job" button is present
        view_job_button = post_element.find_element(By.XPATH, ".//span[contains(@class, 'update-components-button__text') and text()='View job']")
        view_job_button.click()
       
        if view_job_button:
            # Scroll to the view job button to make sure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", view_job_button)
            time.sleep(5)  # Give time for the scroll action
 
            # First, locate the dropdown element by ID
            dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "ember1712")))
 
            # Open the dropdown to reveal the "Copy link" button
            dropdown.click()
 
            #  Wait for the "Copy link" button to be visible and clickable
            copy_link_button = wait.until(EC.element_to_be_clickable((By.XPATH, ".//span[contains(text(), 'Copy link')]")))
 
            # Click the "Copy link" button
            copy_link_button.click()
           
 
            # Fetch the copied job post link (from the clipboard)
            try:
                job_post_link = driver.execute_script("return navigator.clipboard.readText()").strip()
            except:
                job_post_link = "N/A"
 
            # After copying the link and scraping the description, navigate back to the original page
            driver.back()
            time.sleep(5)  # Give time for the original page to load
 
            return job_post_link
    except Exception as e:
        print(f"Error finding or clicking 'View Job' button or scraping content: {e}")
 
    # If "View Job" button is not present, scrape the regular post description
    try:
        post_description = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Click to see more description' and @aria-expanded='false']")))
        post_description.click()
    except Exception as e:
        print(f"Error scraping post description: {e}")
        return None, "N/A"
 
 
# Function to scroll and fetch post descriptions
def scroll_and_scrape_posts(max_posts=20):
    post_data = []  # List to store post data
    posts_scraped = 0
    scroll_attempts = 0
 
    while posts_scraped < max_posts and scroll_attempts < 50:
        # Wait for post containers to load
        try:
            post_containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fie-impression-container")))
        except Exception as e:
            print(f"Error locating post containers: {e}")
            break  # Exit loop if posts can't be found
 
        for post in post_containers[posts_scraped:]:
            if posts_scraped >= max_posts:
                break  # Exit if we have enough posts
           
            try:
                # Scroll post into view
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(5)  # Allow lazy-loading
               
                # Scrape content based on whether it's a job post or a regular post
                post_content = scrape_post_content(post)
               
                # Click on the "More options" (three dots) button
                more_options_button = post.find_element(By.XPATH, ".//button[contains(@aria-label,'Open control menu for post by')]")
                driver.execute_script("arguments[0].click();", more_options_button)
                time.sleep(2)  # Wait for the menu to open
               
                # Click the "Copy link to post" option
                copy_link_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Copy link to post']")))
                copy_link_option.click()
                time.sleep(2)  # Wait for the link to be copied
               
                # Try to retrieve the copied link from the clipboard
                try:
                    post_link = driver.execute_script("return navigator.clipboard.readText()")
                except Exception as e:
                    print(f"Error accessing clipboard: {e}")
                    post_link = "N/A"
                print (post_link)
               
                # Scrape the time posted
                try:
                    time_posted = post.find_element(By.CLASS_NAME, "update-components-actor__sub-description").text
                except Exception as e:
                    print(f"Error scraping time posted: {e}")
                    time_posted = "N/A"
               
                # Scrape the author's name
                try:
                    author_name = post.find_element(By.CLASS_NAME, "update-components-actor__name").text
                except Exception as e:
                    print(f"Error scraping author name: {e}")
                    author_name = "N/A"
               
                # Append the scraped data to the list
                if post_content:
                    post_data.append({
                        "Author Name": author_name,
                        "Post Link": post_link,
                        "Time Posted": time_posted,
                        "Content": post_content
                    })
                    posts_scraped += 1  # Increment the post count
               
            except Exception as e:
                print(f"Error scraping post: {e}")
                continue  # Skip to the next post in case of an error
 
        # Scroll down to load more posts if needed
        if posts_scraped < max_posts:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(5)  # Allow time for new posts to load
            scroll_attempts += 1
 
    return post_data
 
 
 
# Fetch and scrape 20 posts
scraped_posts = scroll_and_scrape_posts(max_posts=20)
 
# Convert scraped data to a pandas DataFrame
df = pd.DataFrame(scraped_posts)
 
# Save the data to an Excel file
df.to_excel("linkedin_posts_scraped.xlsx", index=False)
 
# Close the browser
driver.quit()
 
print("Scraping complete. Data saved to 'linkedin_posts_servicenow.xlsx'.")
 