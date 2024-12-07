from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
show_results_button = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[text()='Show results'])[2]")))
show_results_button.click()

time.sleep(2)

# Function to scrape posts
def scrape_posts_on_page():
    post_data = []
    unique_links = set()  # To track unique post links
    scraped_posts_count = 0

    while scraped_posts_count < 5:
        # Wait for the post containers to load
        wait.until(EC.presence_of_all_elements_located((By.ID, "fie-impression-container")))
        post_containers = driver.find_elements(By.ID, "fie-impression-container")

        for post in post_containers:
            try:
                # Extract author, description, time posted, and post link in the desired order
                author = post.find_element(By.CLASS_NAME, "update-components-actor__name").text
                description = post.find_element(By.CLASS_NAME, "break-words").text
                time_posted_element = post.find_element(By.CLASS_NAME, "update-components-actor__sub-description")
                time_posted = time_posted_element.find_element(By.XPATH, ".//span[@aria-hidden='true']").text
                post_link = post.find_element(By.XPATH, ".//a[@href]").get_attribute("href")

                # Check if the post link is already scraped
                if post_link not in unique_links:
                    unique_links.add(post_link)  # Add the link to the set to avoid duplicates

                    # Append the post details to the list in the desired order
                    post_data.append({
                        "Author": author,
                        "Description": description,
                        "Time Posted": time_posted,
                        "Profile Link": post_link
                    })

                    scraped_posts_count += 1
                    if scraped_posts_count >= 60:
                        break
            except Exception as e:
                print(f"Error scraping post: {e}")
                continue

        # Scroll down to load more posts if necessary
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time based on network speed

    return post_data

# Scrape the posts on the current page
all_post_data = scrape_posts_on_page()

# Convert the data to a pandas DataFrame
post_df = pd.DataFrame(all_post_data)

# Save the data to an Excel file
post_df.to_excel("profile_link.xlsx", index=False)

# Close the browser
driver.quit()

print("Scraping complete.")
