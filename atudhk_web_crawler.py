import urllib3
from bs4 import BeautifulSoup
import pandas as pd


class ATUHKProgrammeCrawler(object):
    def __init__(self):
        self.main_url = 'http://atu.hk/get_programmes.ajax.php?inst=INST&year=YEAR'

    def get_programme_webpage(self, inst: int, year: int):
        url = self.main_url.replace('INST', str(inst)).replace('YEAR', str(year))
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return str(response.data)

    def data_handler(self, text: str):
        text = text.replace("b'[", '').replace(']]', ']').replace('],[', '|')
        text = text.replace('[', '').replace(']', '')
        data_list = text.split("|")
        all_data = list()
        for data in data_list:
            data_row = dict()
            # print(data)
            data = data.replace(',"', '^"')
            code, name = data.split('^')
            data_row['CODE'] = 'JS%s' % code.replace("'", '')
            data_row['NAME'] = name.replace('"', '')
            all_data.append(data_row)
        return all_data

    def main(self):
        colnames_order = ['YEAR', 'INST', 'CODE', 'NAME']
        df_list = list()
        year_range = range(2012, 2018)
        inst_range = range(1, 10)
        for year in year_range:
            for inst in inst_range:
                # print(year, inst)
                text = self.get_programme_webpage(inst, year)
                all_data = self.data_handler(text)
                # print(all_data)
                df = pd.DataFrame(all_data)
                # print(df)
                df['INST'] = [inst for i in range(len(df))]
                df['YEAR'] = [year for i in range(len(df))]
                # print(df)
                df_list.append(df[colnames_order])
                # break
            # break
        return pd.concat(df_list)


class ATUHKRecordIDCrawler(object):
    def __init__(self, file_name='web_source/programme_data.tsv'):
        self.df = pd.read_csv(file_name, sep='\t')
        # print(self.df)

    @staticmethod
    def get_record_webpage(year, code):
        url = 'http://www.atu.hk/adm-grades.php?programme=%s&year=%s' % (code, year)
        # print(url)
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return str(response.data)

    @staticmethod
    def record_id_souping(text: str):
        record = list()
        soup = BeautifulSoup(text, 'lxml')
        soup = soup.find_all({'table': {'class': 'data', 'style': 'font-size:11px;'}})
        if len(soup) == 0:
            return None
        table = soup[0]
        table = table.find_all('tr')
        for row in table:
            row_array = row.find_all('td')
            # print(len(row_array))
            if len(row_array) == 10:
                data_row = dict()
                record_id = str(row_array[0].get_text())
                # banding = row_array[1].get_text()
                english = row_array[2].get_text()
                chinese = row_array[3].get_text()
                maths = row_array[4].get_text()
                liberal_studies = row_array[5].get_text()
                electives = row_array[6].find_all('div', {'class': 'electives'})
                if len(electives) == 1:
                    elective1_sub = electives[0].find_all('div', {'class': 'electives-subj'})[0].get_text()
                    elective1_grade = electives[0].find_all('div', {'class': 'electives-grade'})[0].get_text()
                    elective2_sub = None
                    elective2_grade = None
                else:
                    elective1_sub = electives[0].find_all('div', {'class': 'electives-subj'})[0].get_text()
                    elective1_grade = electives[0].find_all('div', {'class': 'electives-grade'})[0].get_text()
                    elective2_sub = electives[1].find_all('div', {'class': 'electives-subj'})[0].get_text()
                    elective2_grade = electives[1].find_all('div', {'class': 'electives-grade'})[0].get_text()
                best_five = str(row_array[7].get_text())
                # print(record_id, english, chinese, maths, liberal_studies, electives, best_five)
                # print(electives)
                data_row['RECORD_ID'] = record_id
                data_row['BEST_FIVE'] = best_five
                data_row['CHINESE'] = chinese
                data_row['ENGLISH'] = english
                data_row['MATHS'] = maths
                data_row['LIBERAL_STUDIES'] = liberal_studies
                data_row['ELECT_SUB_1'] = elective1_sub
                data_row['ELECT_SUB_2'] = elective2_sub
                data_row['ELECT_GRADE_1'] = elective1_grade
                data_row['ELECT_GRADE_2'] = elective2_grade
                # print(row_array)
                record.append(data_row)
        # print(len(table))
        return record

    def main(self):
        colnames_order = [
            'YEAR', 'CODE', 'RECORD_ID', 'BEST_FIVE', 'CHINESE', 'ENGLISH', 'MATHS',
            'LIBERAL_STUDIES', 'ELECT_SUB_1', 'ELECT_SUB_2', 'ELECT_GRADE_1', 'ELECT_GRADE_2'
        ]
        record_df = list()
        for data in self.df.to_dict('record'):
            # if data['YEAR'] == 2012:
            #     continue
            print('getting ... year = %s, code = %s' % (data['YEAR'], data['CODE']))
            text = self.get_record_webpage(year=data['YEAR'], code=data['CODE'])
            record = self.record_id_souping(text)
            if record is None:
                continue
            df = pd.DataFrame(record)
            df['YEAR'] = [data['YEAR'] for _ in range(len(df))]
            df['CODE'] = [data['CODE'] for _ in range(len(df))]
            record_df.append(df)
            # print(df)
        return pd.concat(record_df)[colnames_order]


if __name__ == '__main__':
    programe_file_name = 'web_source/programme_data.tsv'
    record_file_name = 'web_source/record_data.tsv'
    # atuhk_prog_crawler = ATUHKProgrammeCrawler()
    # programme_df = atuhk_prog_crawler.main()
    # programme_df.to_csv('web_source/programme_data.tsv', sep='\t', index=False)
    atuhk_record_crawler = ATUHKRecordIDCrawler(programe_file_name)
    record_df = atuhk_record_crawler.main()
    record_df.to_csv(record_file_name, sep='\t', index=False)
    print(record_df)
