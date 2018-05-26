#!/usr/bin/python3

from bs4 import BeautifulSoup
import urllib3
import pandas as pd


class JUPASWebCrawler(object):
    def __init__(self):
        self.categories = [
            "Arts+and+Humanities", "Building+and+Architecture", "Business%2C+Management+and+Economics",
            "Communication%2C+Languages%2C+Journalism+and+Broadcasting",
            "Computing%2C+Information+and+Multimedia+Technology", "Education",
            "Engineering", "Fashion+and+Design", "Law", "Medicine%2C+Dentistry+and+Health+Sciences",
            "Music", "Philosophy+and+Religious+Studies", "Science", "Social+Sciences", "Social+Work"
        ]

    @staticmethod
    def generate_url(page_no, category):
        return "https://www.jupas.edu.hk/en/search/?page={0}" \
               "&order_by=&keywords=&study_area[]={1}" \
               "&study_level[]=Bachelor's+Degree&funding[]=UGC-funded".format(page_no, category)

    @staticmethod
    def get_webpage(url):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return str(response.data)

    def main(self):
        all_record = list()
        for cat in self.categories:
            init_page_no = 1
            while True:
                url = self.generate_url(init_page_no, cat)
                webpage_text = self.get_webpage(url)
                soup = BeautifulSoup(webpage_text, 'lxml')
                table = soup.find_all({'table': {"class": "program_table program_table-hasFC"}})
                if len(table) == 0:
                    break
                body = table[0].find_all('tbody')
                row = body[0].find_all('tr')
                for val in row:
                    js_no = val.find_all({'td': {'class': "c-no"}})
                    _no = js_no[1].get_text()
                    all_record.append({
                        'CATEGORIES': cat,
                        'JUPAS_CODE': _no
                    })
                init_page_no += 1
        return pd.DataFrame(all_record)


if __name__ == '__main__':
    jupas_file_name = 'web_source/jupas_category_data.tsv'
    jupas_crawler = JUPASWebCrawler()
    df = jupas_crawler.main()
    df.to_csv(jupas_file_name, sep='\t', index=False)
