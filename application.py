from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for, session
from flask_session import Session
import requests
from bs4 import BeautifulSoup
import re
import unidecode
import pandas as pd
from threading import Thread
import time
from config import SCRAPING_BASE_URL, PORT, HOST, CATEGORY_PAGE
from utils import fetch_course_name_from_course_page, fetch_first_instructor_name_from_course_page, \
    fetch_course_description_from_course_page, fetch_number_of_students_enrolled_from_course_page, \
    fetch_number_of_rating_from_course_page, fetch_all_files_from_directory, generate_csv_file, \
    fetch_course_info_from_course_page

# create a server instance
application = Flask(__name__)
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
Session(application)


@application.route('/<path:filename>', methods=['GET'])
def download(filename):
    # need to check if file exist or not if not exist need to handle error
    return send_from_directory(directory='uploads', path=filename, as_attachment=True)


@application.route('/', methods=('GET', 'POST'))
def home():
    msg = None

    # checking post request or not and then if post request then scrapped the coursera page
    if request.method == 'POST':
        category_name = request.form['category_name']
        category_name_lower_case = unidecode.unidecode(category_name).lower()
        category_slug = re.sub(r'[\W_]+', '-', category_name_lower_case)
        course_list_page = CATEGORY_PAGE + category_slug

        # Fetching course list page data
        course_list_page_content = requests.get(course_list_page)
        soup = BeautifulSoup(course_list_page_content.text, 'html.parser')
        course_list_page_wrapper = soup.find(class_='product-offerings-wrapper')

        # Fetching all link from course list page and filtered by this class [.productCard-title a.CardText-link]
        course_list_page_all_course_link = []
        for a in course_list_page_wrapper.select('.productCard-title a.CardText-link', href=True):
            if a.text:
                # Store all links into a list [course_list_page_all_course_link]
                course_list_page_all_course_link.append(a['href'])

        email_thread = Thread(target=fetch_course_info_from_course_page, args=(course_list_page_all_course_link,
                                                                               category_name, category_slug))
        email_thread.start()
        #fetch_course_info_from_course_page(course_list_page_all_course_link, category_name, category_slug)

        #start
        # Initialize 6 blank list into a variable
        # category_name_list = []
        # course_name_list = []
        # first_instructor_name_list = []
        # course_description_list = []
        # number_of_students_enrolled_list = []
        # number_of_ratings_list = []
        #
        # """
        #     Iterate all links that we already fetched and went through those pages and fetching information
        #     [category name, course name, first instructor name, number of students enrolled, number of ratings]
        #  """
        # for single_course_link in course_list_page_all_course_link:
        #     url = SCRAPING_BASE_URL + single_course_link
        #
        #     # Fetch all information from individual course page
        #     single_course_page_content = requests.get(url)
        #     single_course_page_content_text = BeautifulSoup(single_course_page_content.text, 'html.parser')
        #
        #     # Store category name into category_name_list variable
        #     category_name_list.append(category_name)
        #
        #     # Fetching course name
        #     course_name = fetch_course_name_from_course_page(single_course_page_content_text)
        #     course_name_list.append(course_name)
        #
        #     # Fetching first instructor name
        #     first_instructor_name = fetch_first_instructor_name_from_course_page(single_course_page_content_text)
        #     first_instructor_name_list.append(first_instructor_name)
        #
        #     # Fetching course description
        #     course_description = fetch_course_description_from_course_page(single_course_page_content_text)
        #     course_description_list.append(course_description)
        #
        #     # Fetching number of students enrolled from course page
        #     number_of_students_enrolled = fetch_number_of_students_enrolled_from_course_page(single_course_page_content_text)
        #     number_of_students_enrolled_list.append(number_of_students_enrolled)
        #
        #     # Fetching number of ratings from course page
        #     number_of_ratings = fetch_number_of_rating_from_course_page(single_course_page_content_text)
        #     number_of_ratings_list.append(number_of_ratings)
        #     #time.sleep(0.1)
        #
        # course_dict = {
        #     'Category Name': category_name_list,
        #     'Course Name': course_name_list,
        #     '# of Students Enrolled': number_of_students_enrolled_list,
        #     '# of Ratings': number_of_ratings_list,
        # }
        #
        # # Generate CSV file
        # generate_csv_file(course_dict, category_slug)

        #end
        msg = "Your CSV file {} is being generated. After the file is ready it will automatically fetch the CSV file."\
            .format(category_name)
        #return redirect("/")

    files_dict = fetch_all_files_from_directory()

    # check course category list exist on session variable.
    if session.get("course_category_list_session"):
        course_category_list = session.get("course_category_list_session")
        course_category_list = list(course_category_list.split("-"))

        return render_template('home.html', number_of_course_category=len(course_category_list)
                               , course_category_list=course_category_list, files_dict=files_dict, msg=msg)

    category_page_content = requests.get(CATEGORY_PAGE)
    soup = BeautifulSoup(category_page_content.text, 'html.parser')
    course_category_wrapper = soup.find(class_='topic-skills-wrapper')
    course_category_items = course_category_wrapper.select('.domain-card-name span')

    course_category_list = []
    for course_category in course_category_items:
        course_category_name = course_category.contents
        course_category_list.extend(course_category_name)

    course_category_list_string = '-'.join(course_category_list)
    session["course_category_list_session"] = course_category_list_string

    return render_template('home.html', number_of_course_category=len(course_category_list),
                           course_category_list=course_category_list, files_dict=files_dict, msg=msg)


if __name__ == '__main__':
    application.run(port=PORT, host=HOST)
