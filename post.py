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
# Function to scrape posts on the current page and fetch the post link
def scrape_posts_on_page():
    post_data = []
   
    # Wait for the post containers to load
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"fie-impression-container")))
    #wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "reusable-search__result-container")))
   
    # Find all post containersn
    post_containers = driver.find_elements(By.CLASS_NAME,"fie-impression-container")
   
   
    tag_count = len(post_containers)
   
    print(tag_count)    
   
    #post_containers = driver.find_elements(By.CLASS_NAME, "reusable-search__result-container")
   
    for post in post_containers:
        try:
           
            #print(post)  
           
            # Click the three-dot menu (overflow menu)
            #more_options_button =wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@aria-label,'Open control menu for post by')])[{post}]")))
            more_options_button =wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(@aria-label,'Open control menu for post by')])")))
            more_options_button.click()
            time.sleep(2)  # Wait for the menu to appear
 
            # Click on the "Copy link to post" option
            copy_link_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Copy link to post']")))
            copy_link_option.click()
            time.sleep(2)  # Wait for the link to be copied
 
            # Get the copied link from the clipboard (this may require an alternative method as clipboard access is restricted in some environments)
            post_link = driver.execute_script("return navigator.clipboard.readText()")
            print(post_link)
 
            # Append the post details to the list
            post_data.append({
                # "Author": author,
                # "Post Text": post_text,
                # "Timestamp": timestamp,
                "Post Link": post_link
            })
 
            # Close the options menu (if necessary)
            close_modal_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
            close_modal_button.click()
            time.sleep(2)
       
        except Exception as e:
            print(f"Error scraping post: {e}")
            continue
   
    return post_data
 
 # Scrape the posts on the current page
all_post_data = scrape_posts_on_page()
 
# Convert the data to a pandas DataFrame
post_df = pd.DataFrame(all_post_data)
 
# Save the data to an Excel file
post_df.to_excel("post.xlsx", index=False)
 
# Close the browser
driver.quit()
 
print("Scraping complete.")