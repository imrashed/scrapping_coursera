# Fetching course name
import os

import pandas as pd

from config import CATEGORY_PAGE


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
    df.to_csv("uploads/" + file_name)


