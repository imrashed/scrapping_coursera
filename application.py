from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for, session
from flask_session import Session
import requests
from bs4 import BeautifulSoup
import re
import unidecode
import pandas as pd
import os
import time
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
def home():  # put application's code here
    scrapping_base_url = "https://www.coursera.org"
    category_page = scrapping_base_url + '/browse/'

    # checking post request or not and then if post request then scrapped the coursera page
    if request.method == 'POST':
        category_name = request.form['category_name']
        category_name_lower_case = unidecode.unidecode(category_name).lower()
        category_slug = re.sub(r'[\W_]+', '-', category_name_lower_case)
        course_list_page = category_page + category_slug

        course_list_page_content = requests.get(course_list_page)
        soup = BeautifulSoup(course_list_page_content.text, 'html.parser')
        course_list_page_wrapper = soup.find(class_='product-offerings-wrapper')

        course_list_page_all_course_link = []
        for a in course_list_page_wrapper.select('.productCard-title a.CardText-link', href=True):
            if a.text:
                course_list_page_all_course_link.append(a['href'])

        category_name_list = []
        course_name_list = []
        first_instructor_name_list = []
        course_description_list = []
        number_of_students_enrolled_list = []
        number_of_ratings_list = []

        for single_course_link in course_list_page_all_course_link:
            url = scrapping_base_url + single_course_link
            single_course_page_content = requests.get(url)
            print(url)
            soup = BeautifulSoup(single_course_page_content.text, 'html.parser')

            category_name_list.append(category_name)

            # getting course name
            try:
                course_name = soup.select_one('h1').text
            except Exception as e:
                course_name = "No title found"
                print(e)
            course_name_list.append(course_name)

            # getting first instructor name
            try:
                first_instructor_name = soup.select_one('div.rc-BannerInstructorInfo span').text.split('+')
                first_instructor_name = first_instructor_name[0]
            except Exception as e:
                first_instructor_name = "No Instructor found"
                print(e)
            first_instructor_name_list.append(first_instructor_name)

            # getting course description
            try:
                course_description = soup.select_one('.description').text
            except Exception as e:
                course_description = 'No description found'
                print(e)
            course_description_list.append(course_description)

            # getting number of students enrolled
            try:
                number_of_students_enrolled = soup.select_one('.rc-ProductMetrics').text.replace("already enrolled", "")
            except Exception as e:
                number_of_students_enrolled = 'None'
                print(e)
            number_of_students_enrolled_list.append(number_of_students_enrolled)

            # getting number of ratings
            try:
                number_of_ratings = soup.select_one('.ratings-count-expertise-style span span').\
                    text.replace("ratings", "")
            except Exception as e:
                number_of_ratings = 'None'
                print(e)
            number_of_ratings_list.append(number_of_ratings)
            time.sleep(0.5)

        course_dict = {
            'Category Name': category_name_list,
            'Course Name': course_name_list,
            '# of Students Enrolled': number_of_students_enrolled_list,
            '# of Ratings': number_of_ratings_list,
        }

        df = pd.DataFrame(course_dict)
        file_name = category_slug + ".csv"
        df.to_csv("uploads/" + file_name)
        return redirect("/")

    # scan the directory and getting all files name
    file_obj = [{"course_category_name": x.name.replace(".csv", "").replace("-", " ").title(), "course_category_url":
        x.name} for x in os.scandir("uploads")]

    # check course category list exist on session variable.
    # if session.get("course_category_list"):
    #     course_category_list = session.get("course_category_list")
    #     return render_template('home.html', number_of_course_category=len(course_category_list),
    #                        course_category_list=course_category_list, file_obj=file_obj)

    category_page_content = requests.get(category_page)
    soup = BeautifulSoup(category_page_content.text, 'html.parser')
    course_category_wrapper = soup.find(class_='topic-skills-wrapper')
    course_category_items = course_category_wrapper.select('.domain-card-name span')

    course_category_list = []
    for course_category in course_category_items:
        course_category_name = course_category.contents
        course_category_list.extend(course_category_name)

    #session["course_category_list"] = course_category_list
    # session["course_category_list_session"] = 5
    #print(type(course_category_list))
    return render_template('home.html', number_of_course_category=len(course_category_list),
                           course_category_list=course_category_list, file_obj=file_obj)


if __name__ == '__main__':
    application.run(port=80, host='0.0.0.0')
