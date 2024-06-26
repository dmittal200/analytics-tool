import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

class FinancialForecaster:
    def __init__(self, data):
        self.data = data
        self.model = LinearRegression()

    def preprocess_data(self):
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data['month'] = self.data['date'].dt.month
        self.data['year'] = self.data['date'].dt.year
        
        # Fill NaN values with 0
        self.data = self.data.fillna(0)
        
        return self.data

    def train_model(self):
        self.data = self.preprocess_data()
        X = self.data[['month', 'year']]
        y = self.data['profit']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        return score if score is not None else 0.0


    def forecast(self, future_data):
        future_data['date'] = pd.to_datetime(future_data['date'])
        future_data['month'] = future_data['date'].dt.month
        future_data['year'] = future_data['date'].dt.year

        # Fill NaN values with 0 in future data
        future_data = future_data.fillna(0)

        predictions = self.model.predict(future_data[['month', 'year']])
        return predictions
