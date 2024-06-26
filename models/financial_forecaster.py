import pandas as pd
import numpy as np
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

    def forecast(self, future_dates):
        future_dates['date'] = pd.to_datetime(future_dates['date'])
        future_dates['month'] = future_dates['date'].dt.month
        future_dates['year'] = future_dates['date'].dt.year

        # Fill NaN values with 0 in future data
        future_dates = future_dates.fillna(0)

        predictions = self.model.predict(future_dates[['month', 'year']])
        return predictions

    def generate_scenario(self, base_data, revenue_growth_rate=0, expense_change_factor=1):
        scenario_data = base_data.copy()

        # Adjust revenue based on growth rate
        scenario_data['revenue'] = base_data['revenue'] * (1 + revenue_growth_rate)

        # Adjust expenses based on expense change factor
        scenario_data['expenses'] = base_data['expenses'] * expense_change_factor

        # Recalculate profit based on adjusted revenue and expenses
        scenario_data['profit'] = scenario_data['revenue'] - scenario_data['expenses']

        return scenario_data
