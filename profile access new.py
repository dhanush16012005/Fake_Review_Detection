#!/usr/bin/env python
# coding: utf-8

# In[51]:


import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time

class ReviewsScraper:
    MAX_RETRIES = 3

    def __init__(self, product_url: str):
        self.product_url = product_url
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.processed_users = set()

    def get_reviews_from_page(self, page_number: int) -> List[dict]:
        reviews = []
        url = f'{self.product_url}&pageNumber={page_number}'
        self.driver.get(url)

        # Find the main review container
        main_container = self.driver.find_element("css selector", 'div.a-section.a-spacing-none.reviews-content.a-size-base')

        # Find review containers within the main container
        review_containers = main_container.find_elements("css selector", 'div[data-hook=genome-widget]')

        for container in review_containers:
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    username_element = container.find_element("css selector", 'span[class=a-profile-name]')
                    username = username_element.text
                    print(f"Processing user: {username}")

                    # Check if the user is already processed, skip if yes
                    if username in self.processed_users:
                        retries += 1
                        continue

                    self.processed_users.add(username)

                    # Navigate to the user profile link to extract more reviews
                    user_profile_link_element = container.find_element("css selector", 'a[class=a-profile]')
                    user_profile_link = user_profile_link_element.get_attribute('href')
                    self.driver.get(user_profile_link)

                    # Add a delay to allow the page to load
                    time.sleep(2)

                    # Collect reviews on the user profile page
                    user_reviews = self.collect_reviews_on_user_profile_page()

                    reviews.append({
                        'username': username,
                        'user_reviews': user_reviews
                    })
                    break
                except StaleElementReferenceException:
                    print("Stale element reference. Retrying...")
                    retries += 1
                    continue
                except Exception as e:
                    print(f"Error extracting review: {e}")
                    break

        return reviews

    def collect_reviews_on_user_profile_page(self) -> List[dict]:
        user_reviews = []

        # Update the selector to target the reviews within the specified container
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'your-content-card-column'))
        )

        # Find reviews within the specified container
        reviews_container = self.driver.find_elements("css selector", 'div.your-content-card-column')

        for review in reviews_container:
            try:
                rating_element = review.find_element("css selector", 'i[class*=a-icon-star]')
                rating = rating_element.get_attribute('textContent')
                title = review.find_element("css selector", 'h1[class*=your-content-title]').text
                content = review.find_element("css selector", 'p[class*=your-content-text-3]').text

                user_reviews.append({
                    'rating': rating,
                    'title': title,
                    'content': content
                })
            except NoSuchElementException:
                # Handle the case where a required element is not found
                print("Error extracting review: Required element not found")

        return user_reviews

    def has_reviews(self) -> bool:
        return bool(self.driver.find_elements("css selector", 'div.a-section.a-spacing-none.reviews-content.a-size-base'))

    def iterate_over_reviews(self):
        all_reviews = []

        for _ in range(10):
            page_number = 1
            while True:
                print(f"Processing reviews on page {page_number}")
                reviews_on_page = self.get_reviews_from_page(page_number)

                if not reviews_on_page:
                    print("No reviews found on this page.")
                    break

                print("New reviews")
                print(reviews_on_page)
                all_reviews += reviews_on_page

                # Move to the next page
                page_number += 1

        self.save_to_file(all_reviews)


    def save_to_file(self, reviews: List[dict]):
        with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'user_reviews']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header
            writer.writeheader()

            # Write the reviews
            for review in reviews:
                writer.writerow({
                    'username': review['username'],
                    'user_reviews': str(review['user_reviews'])  # Convert to string to write as a single cell
                })

if __name__ == '__main__':
    product_url = 'https://www.amazon.in/EASYSHOP-Magnetic-Replacement-Charging-Colourfit/product-reviews/B09HC2QQZ2/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews%27'
    scraper = ReviewsScraper(product_url)
    scraper.iterate_over_reviews()
    print("Done.")


# In[ ]:





# In[ ]:




