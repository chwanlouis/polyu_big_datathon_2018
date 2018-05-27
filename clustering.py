import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


class PCAPreprocessor(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.df = pd.read_csv(self.file_name, sep='\t')
        self.all_elective_sub = self.get_all_elective_subject()

    def get_all_elective_subject(self):
        elec1 = self.df['ELECT_SUB_1'].values.tolist()
        elec2 = self.df['ELECT_SUB_2'].values.tolist()
        combine_list = list(set(elec1 + elec2))
        combine_list = [ele for ele in combine_list if type(ele) == str]
        return combine_list

    def build_features(self):
        elect_sub_1 = self.df['ELECT_SUB_1'].values.tolist()
        elect_sub_2 = self.df['ELECT_SUB_2'].values.tolist()
        elect_grade_1 = self.df['ELECT_GRADE_1'].values.tolist()
        elect_grade_2 = self.df['ELECT_GRADE_2'].values.tolist()
        for feature in self.all_elective_sub:
            new_list = list()
            for elec1, elec2, grad1, grad2 in zip(elect_sub_1, elect_sub_2, elect_grade_1, elect_grade_2):
                if elec1 == feature:
                    new_list.append(grad1)
                elif elec2 == feature:
                    new_list.append(grad2)
                else:
                    new_list.append(0)
            self.df[feature] = new_list

    @staticmethod
    def grade_transform(grade):
        grade = str(grade)
        if grade == '5**':
            return 7
        elif grade == '5*':
            return 6
        elif grade == '5':
            return 5
        elif grade == '4':
            return 4
        elif grade == '3':
            return 3
        elif grade == '2':
            return 2
        elif grade == '1':
            return 1
        else:
            return 0

    def main(self):
        self.build_features()
        self.cat_df = pd.read_csv('web_source/jupas_category_data.tsv', sep='\t')
        self.cat_df['JUPAS_CODE'] = [code.replace('\n', '') for code in self.cat_df['JUPAS_CODE']]
        features = ['CHINESE', 'ENGLISH', 'MATHS', 'LIBERAL_STUDIES'] + self.all_elective_sub
        df = self.df[features]
        for feature in features:
            df[feature] = [self.grade_transform(grade) for grade in df[feature]]
        code = self.df['CODE']
        cat = list()
        for _code in code:
            selected_df = self.cat_df[self.cat_df['JUPAS_CODE'] == _code]
            cat_name = selected_df['CATEGORIES']
            if len(cat_name) > 0:
                cat.append(cat_name.values[0])
            else:
                cat.append(None)
        return df, code.values.tolist(), cat


class PricipleComponentAnalysis(object):
    def __init__(self, X):
        self.X = X
        # print(self.X.shape)
        self.model = PCA(n_components=10).fit(self.X)
        # print(self.model.explained_variance_ratio_)
        # print('???????????????')
        self.output = self.model.transform(self.X)


class ClusteringAlgorithm(object):
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.n_class = len(set(self.y))

    def build_model(self, n_class):
        model = KMeans(n_class)
        return model.fit(self.X)

    def main(self):
        for n_class in range(self.n_class-5, self.n_class+6):
            model = self.build_model(n_class)
            y_pred = model.predict(self.X)
            score = silhouette_score(self.X, y_pred)
            print('N_CLASS = %s , score = %s' % (n_class, score))


if __name__ == '__main__':
    file_name = 'web_source/record_data.tsv'
    preprocessor = PCAPreprocessor(file_name)
    df, y_code, y_cat = preprocessor.main()
    X = df.values
    pca = PricipleComponentAnalysis(X)
    output = pca.output
    model = ClusteringAlgorithm(X, y_cat)
    model.main()
