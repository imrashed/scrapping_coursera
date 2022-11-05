import os

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

        # Fetching course info from every page by a new thread
        fetching_course_info_thread = Thread(target=fetch_course_info_from_course_page,
                                             args=(course_list_page_all_course_link, category_name, category_slug))
        fetching_course_info_thread.start()
        msg = "Your CSV file {} is being generated. After the file is ready it will automatically fetch the CSV file."\
            .format(category_name)

    # Creating upload folder for CSV file upload
    if not os.path.exists("uploads"):
        os.mkdir("uploads")

    # Fetch all files from uploads directory
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
