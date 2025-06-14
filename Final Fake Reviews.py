#!/usr/bin/env python
# coding: utf-8

# In[19]:


import csv

def find_fake_reviews(file_path='results.csv'):
    # Dictionary to store user reviews
    user_reviews_dict = {}

    # Set to store usernames with potential fake reviews
    users_with_fake_reviews = set()

    # Read the CSV file
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Iterate through each row in the CSV file
        for row in reader:
            username = row['username']
            user_reviews = eval(row['user_reviews'])  # Convert string to list of dictionaries

            # Check for repeated content within the user
            for review in user_reviews:
                content = review['content']
                user_content_pair = (username, content)

                if user_content_pair in user_reviews_dict:
                    # If user content pair is already seen, add the user to the set
                    users_with_fake_reviews.add(username)
                else:
                    user_reviews_dict[user_content_pair] = True

    # Print the number of users with potential fake reviews
    num_users_with_fake_reviews = len(users_with_fake_reviews)
    print(f"Number of users with potential fake reviews: {num_users_with_fake_reviews}")

    # Print usernames with potential fake reviews
    if users_with_fake_reviews:
        print(f"Usernames with potential fake reviews:")
        for username in users_with_fake_reviews:
            print(username)
    else:
        print("No potential fake reviews found.")

if __name__ == '__main__':
    find_fake_reviews()


# In[ ]:




