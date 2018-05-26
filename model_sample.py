import pandas as pd
# from sklearn.linear_model import LinearRegression
import statsmodels.api as sm


class MultivariateRegressionModel(object):
    def __init__(self, df, features, responses):
        self.features = features
        self.features_colnames = sorted(list(self.features.keys()))
        self.responses = responses
        self.df = df
        self.features_type_reform()
        self.test_df, self.train_df = self.df[:18], self.df[18:]
        self.train_X, self.train_y = self.features_regressors_split(self.train_df)
        self.test_X, self.test_y = self.features_regressors_split(self.test_df)

    def features_type_reform(self):
        for feature, data_type in self.features.items():
            self.df[feature] = self.df[feature].apply(data_type)
        self.df = self.df[self.features_colnames + self.responses]
        self.df = pd.get_dummies(self.df)
        self.updated_features_colnames = [col for col in sorted(self.df.columns.values.tolist()) if col not in self.responses]

    def features_regressors_split(self, df):
        X = df[self.updated_features_colnames]
        # print(X)
        y = df[self.responses]
        # print(X)
        return X.values, y.values

    def model_training(self, y, X):
        glm = sm.GLM(y, X, family=sm.families.Gaussian())
        return glm.fit()

    def main(self):
        # print(self.train_y.shape)
        # print(self.train_X.shape)
        model = self.model_training(self.train_y, self.train_X)
        print(model.summary())

if __name__ == '__main__':
    file_name = 'dataset/preprocessed_JupasAdmData.csv'
    df = pd.read_csv(file_name)
    features = {
        'Year': str, 'BAND_A_APPL': float, 'BAND_A_OFFER': float, 'ATU_MAX': float, 'ATU_MIN': float,
        'ATU_AVG': float, 'Average': float, 'is_science': float, 'is_BBA': float, 'is_nursing': float,
        'is_engineering': float
    }
    # regs = ['UpperQ', 'Median', 'LowerQ']
    regs = ['UpperQ']
    model = MultivariateRegressionModel(df, features, regs)
    # print(model.test_X)
    model.main()
