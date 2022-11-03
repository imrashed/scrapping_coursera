from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for, session
from flask_session import Session
import requests
from bs4 import BeautifulSoup
import re
import unidecode
import pandas as pd
import os

# create a server instance
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/<path:filename>', methods=['GET'])
def download(filename):
    # need to check if file exist or not if not exist need to handle error
    return send_from_directory(directory='uploads', path=filename, as_attachment=True)

@app.route('/', methods=('GET', 'POST'))
def home():  # put application's code here
    scrapping_base_url = "https://www.coursera.org/"
    category_page = scrapping_base_url + 'browse/'
    if 'course_category_wrapper_session' not in session:
        category_page_content = requests.get(category_page)
        soup = BeautifulSoup(category_page_content.text, 'html.parser')
        course_category_wrapper = soup.find(class_='topic-skills-wrapper')
        session["course_category_wrapper_session"] = course_category_wrapper
    else:
        print('session has')
        course_category_wrapper = session['course_category_wrapper_session']

    course_category_items = course_category_wrapper.select('.domain-card-name span')

    file_obj = [{"course_category_name": x.name.replace(".csv", "").replace("-", " ").title(), "course_category_url":
            x.name} for x in os.scandir("uploads")]

    if request.method == 'POST':
        category_list = request.form['category_list']
        category_list_lower_case = unidecode.unidecode(category_list).lower()
        category_slug = re.sub(r'[\W_]+', '-', category_list_lower_case)
        category_page_single = category_page + category_slug
        print(category_page_single)

        name_dict = {
            'Name': ['a', 'b', 'c', 'd'],
            'Score': [90, 80, 95, 20]
        }

        df = pd.DataFrame(name_dict)
        file_name = category_slug + ".csv"
        df.to_csv("uploads/" + file_name)
        print(df)
        return redirect("/")
        # return render_template('home.html', file_names=file_obj)

    course_category_list = []
    for course_category in course_category_items:
        course_category_name = course_category.contents
        course_category_list.extend(course_category_name)
    return render_template('home.html', number_of_course_category=len(course_category_list),
                           course_category_list=course_category_list, file_obj=file_obj)


if __name__ == '__main__':
    app.run()
