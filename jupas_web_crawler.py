#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests

categories = ["Arts+and+Humanities", "Building+and+Architecture", "Business%2C+Management+and+Economics",
              "Communication%2C+Languages%2C+Journalism+and+Broadcasting",
              "Computing%2C+Information+and+Multimedia+Technology", "Education",
              "Engineering", "Fashion+and+Design", "Law", "Medicine%2C+Dentistry+and+Health+Sciences",
              "Music", "Philosophy+and+Religious+Studies", "Science", "Social+Sciences", "Social+Work"]


page_no = 1
selected_cat = categories[0]


url = "https://www.jupas.edu.hk/en/search/?page={0}" \
      "&order_by=&keywords=&study_area[]={1}" \
      "&study_level[]=Bachelor's+Degree&funding[]=UGC-funded".format(page_no, selected_cat)

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")


