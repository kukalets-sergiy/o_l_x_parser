import time
from selenium import webdriver
from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

path_to_chromedriver = '/user/local/bin/chromedriver'
options = webdriver.ChromeOptions
driver = webdriver.Chrome()
service = Service(path_to_chromedriver)
base_url = "https://www.olx.ua/uk/"
driver.get(base_url)
wait = WebDriverWait(driver, 15)

# Locate categories
categories_xpath = '//div[@data-testid="home-categories-menu-row"]/a/span'
category_xpath = '//div[@data-testid="home-categories-menu-row"]//a[@data-path]'
like_elements_xpath = '//div[@data-testid="favorite-icon"]'
cookies_overlay_xpath = '//div[@data-testid="cookies-overlay__container"]'

# Wait for categories to be present
category_elements_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, category_xpath)))
# Extract the data-path attribute values
category_paths_list = [element.get_attribute("data-path") for element in category_elements_list]
# Select a random category path
random_category_path = random.choice(category_paths_list)
# Compose the URL with the random category path
full_url = base_url + random_category_path
# Navigate to the composed URL
driver.get(full_url)
print(f"Random category path: {random_category_path}")

time.sleep(10)

# Wait for like elements to be present
like_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, like_elements_xpath)))

# Process and like the first 10 elements
for index in range(min(10, len(like_elements))):
    try:
        # Re-fetch the like elements list if necessary
        like_elements = driver.find_elements(By.XPATH, like_elements_xpath)
        like_element = like_elements[index]

        # Output the text of the like element for verification
        print(f"Like element {index + 1}: {like_element.text}")

        # Click on the like element to subscribe
        like_element.click()
        time.sleep(1)  # Optional, adjust as needed

    except StaleElementReferenceException:
        print(f"StaleElementReferenceException encountered on element {index + 1}, retrying...")
        like_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, like_elements_xpath)))
        like_element = like_elements[index]
        like_element.click()

    except ElementClickInterceptedException:
        print(f"ElementClickInterceptedException encountered on element {index + 1}, handling...")
        # Wait for the cookies overlay to disappear
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.XPATH, cookies_overlay_xpath))
        )
        # Re-fetch like elements and click again
        like_elements = driver.find_elements(By.XPATH, like_elements_xpath)
        like_element = like_elements[index]
        like_element.click()

# Wait for the listing grid to load
wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="listing-grid"]//div[@data-testid="l-card"]')))

# Find item titles and prices
item_prices = driver.find_elements(By.XPATH, '//p[@data-testid="ad-price"]')
item_titles = driver.find_elements(By.XPATH, '//div[@data-testid="l-card"]')

for item_title, item_price in zip(item_titles, item_prices):
    title = item_title.text.split('\n')[1] if 'ТОП' in item_title.text else item_title.text.split('\n')[0]
    price = item_price.text.split('\n')[0]

    print(f"Title: {title} \nPrice: {price}")

driver.quit()
