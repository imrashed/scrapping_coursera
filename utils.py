# Fetching course name
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup
from config import CATEGORY_PAGE, SCRAPING_BASE_URL


def fetch_course_name_from_course_page(single_course_page_content_text):
    try:
        course_name = single_course_page_content_text.select_one('h1').text
    except Exception as e:
        course_name = "No title found"
        print(e)
    return course_name


# Fetching first instructor name
def fetch_first_instructor_name_from_course_page(single_course_page_content_text):
    try:
        first_instructor_name = single_course_page_content_text.select_one(
            'div.rc-BannerInstructorInfo span').text.split('+')
        first_instructor_name = first_instructor_name[0]
    except Exception as e:
        first_instructor_name = "No Instructor found"
        print(e)
    return first_instructor_name


# Fetching Course description
def fetch_course_description_from_course_page(single_course_page_content_text):
    try:
        course_description = single_course_page_content_text.select_one('.description').text
    except Exception as e:
        course_description = 'No description found'
        print(e)
    return course_description


# Fetching number of students enrolled from course page
def fetch_number_of_students_enrolled_from_course_page(single_course_page_content_text):
    try:
        number_of_students_enrolled = single_course_page_content_text.select_one('.rc-ProductMetrics').text\
            .replace("already enrolled", "")
    except Exception as e:
        number_of_students_enrolled = 'None'
        print(e)
    return number_of_students_enrolled


# Fetching number of ratings from course page
def fetch_number_of_rating_from_course_page(single_course_page_content_text):
    try:
        number_of_ratings = single_course_page_content_text.select_one('.ratings-count-expertise-style span span'). \
            text.replace("ratings", "")
    except Exception as e:
        number_of_ratings = 'None'
        print(e)
    return number_of_ratings


# Fetch all files from directory
def fetch_all_files_from_directory():
    files_dict = [{"course_category_name": x.name.replace(".csv", "").replace("-", " ").title(),
                   "course_category_url": x.name} for x in os.scandir("uploads")]
    return files_dict


# Generate CSV file
def generate_csv_file(data, file_name):
    df = pd.DataFrame(data)
    file_name = file_name + ".csv"
    if not os.path.exists("uploads"):
        os.mkdir("uploads")
    df.to_csv("uploads/" + file_name)


def fetch_course_info_from_course_page(course_list_page_all_course_link, category_name, category_slug):
    # Initialize 6 blank list into a variable
    category_name_list = []
    course_name_list = []
    first_instructor_name_list = []
    course_description_list = []
    number_of_students_enrolled_list = []
    number_of_ratings_list = []

    """  
        Iterate all links that we already fetched and went through those pages and fetching information
        [category name, course name, first instructor name, number of students enrolled, number of ratings]
     """
    for single_course_link in course_list_page_all_course_link:
        url = SCRAPING_BASE_URL + single_course_link

        # Fetch all information from individual course page
        single_course_page_content = requests.get(url)
        single_course_page_content_text = BeautifulSoup(single_course_page_content.text, 'html.parser')

        # Store category name into category_name_list variable
        category_name_list.append(category_name)

        # Fetching course name
        course_name = fetch_course_name_from_course_page(single_course_page_content_text)
        course_name_list.append(course_name)

        # Fetching first instructor name
        first_instructor_name = fetch_first_instructor_name_from_course_page(single_course_page_content_text)
        first_instructor_name_list.append(first_instructor_name)

        # Fetching course description
        course_description = fetch_course_description_from_course_page(single_course_page_content_text)
        course_description_list.append(course_description)

        # Fetching number of students enrolled from course page
        number_of_students_enrolled = fetch_number_of_students_enrolled_from_course_page(
            single_course_page_content_text)
        number_of_students_enrolled_list.append(number_of_students_enrolled)

        # Fetching number of ratings from course page
        number_of_ratings = fetch_number_of_rating_from_course_page(single_course_page_content_text)
        number_of_ratings_list.append(number_of_ratings)
        # time.sleep(0.1)

    course_dict = {
        'Category Name': category_name_list,
        'Course Name': course_name_list,
        '# of Students Enrolled': number_of_students_enrolled_list,
        '# of Ratings': number_of_ratings_list,
    }

    # Generate CSV file
    generate_csv_file(course_dict, category_slug)

