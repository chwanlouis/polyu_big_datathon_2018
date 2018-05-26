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


if __name__ == '__main__':
    atuhk_prog_crawler = ATUHKProgrammeCrawler()
    programme_df = atuhk_prog_crawler.main()
    programme_df.to_csv('web_source/programme_data.tsv', sep='\t', index=False)