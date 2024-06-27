import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from sqlalchemy import create_engine
from config import Config
from database.models import FinancialData
from models.financial_forecaster import FinancialForecaster
from models.financial_ratios import calculate_profitability_ratios, calculate_liquidity_ratios, calculate_leverage_ratios
from pandas.tseries.offsets import DateOffset

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

# Connect to the database
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
data = pd.read_sql('financial_data', engine)

# Calculate financial ratios
data = calculate_profitability_ratios(data)
data = calculate_liquidity_ratios(data)
data = calculate_leverage_ratios(data)

# Initialize the forecasting model
forecaster = FinancialForecaster(data)

# Train the model and calculate model score
try:
    model_score = forecaster.train_model()
except Exception as e:
    print(f"Error training model: {e}")
    model_score = None

# Define app layout with Bootstrap navbar and adjusted tab sizes
app.layout = html.Div([
    html.Nav([
        html.A('Financial Forecasting and Scenario Analysis Tool', className='navbar-brand text-white'),

        dcc.Tabs(id='tabs', value='tab-dashboard', children=[
            dcc.Tab(label='Dashboard', value='tab-dashboard', className='nav-item'),
            dcc.Tab(label='Forecast', value='tab-forecast', className='nav-item'),
            dcc.Tab(label='Scenario Analysis', value='tab-scenario', className='nav-item')
        ], className='nav nav-tabs ml-auto')
    ], className='navbar navbar-expand-lg navbar-dark bg-dark'),

    html.Div(id='tab-content', className='container-fluid tab-content')
])

# Callback to update tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value')]
)
def render_tab_content(tab):
    if tab == 'tab-dashboard':
        return html.Div([
            html.H2('Historical Data Visualization', className='mb-4 bg-light'),
            dcc.Graph(
                id='historical-data',
                figure={
                    'data': [
                        {'x': data['date'], 'y': data['revenue'], 'type': 'line', 'name': 'Revenue'},
                        {'x': data['date'], 'y': data['expenses'], 'type': 'line', 'name': 'Expenses'},
                        {'x': data['date'], 'y': data['profit'], 'type': 'line', 'name': 'Profit'},
                    ],
                    'layout': {
                        'title': 'Historical Financial Data'
                    }
                }
            ),

            html.Div([
                html.H2('Financial Ratios', className='mt-5'),
                dcc.Markdown(f"""
                **Profitability Ratios:**
                - Profit Margin: {data['profit_margin'].iloc[-1]:.2%}
                - Return on Assets: {data['return_on_assets'].iloc[-1]:.2%}
                - Return on Equity: {data['return_on_equity'].iloc[-1]:.2%}

                **Liquidity Ratios:**
                - Current Ratio: {data['current_ratio'].iloc[-1]:.2f}
                - Quick Ratio: {data['quick_ratio'].iloc[-1]:.2f}

                **Leverage Ratios:**
                - Debt to Equity Ratio: {data['debt_to_equity_ratio'].iloc[-1]:.2f}
                - Interest Coverage Ratio: {data['interest_coverage_ratio'].iloc[-1]:.2f}
                """, className='bg-light p-3')
            ], className='mt-4')
        ], className='p-4 bg-white rounded')

    elif tab == 'tab-forecast':
        return html.Div([
            html.H2('Forecasting Section', className='mb-4'),
            html.Div([
                html.Label('Select Future Dates:'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=data['date'].max(),
                    end_date=(pd.to_datetime(data['date'].max()) + DateOffset(months=6)).strftime('%Y-%m-%d')
                ),
                html.Button('Forecast', id='forecast-button', n_clicks=0, className='btn btn-dark mt-1 ml-2'),
            ]),
            dcc.Graph(id='forecasted-data', className='mt-4'),

            html.Div(id='model-score', children=f'Model Accuracy: {model_score * 100:.2f}%' if model_score is not None else 'Model score not available', className='mt-4 bg-info text-white p-3')
        ], className='p-4 bg-light rounded')

    elif tab == 'tab-scenario':
        return html.Div([
                html.H2('Scenario Analysis', className='mb-4'),
                html.Div([
                    html.Label('Scenario Analysis:'),
                    dcc.Dropdown(
                        id='scenario-dropdown',
                        options=[
                            {'label': 'Base Case', 'value': 'base'},
                            {'label': 'Best Case', 'value': 'best', 'disabled': False},
                            {'label': 'Worst Case', 'value': 'worst', 'disabled': False},
                        ],
                        value='base',
                        clearable=False,
                        className='form-control',  # This is a Bootstrap class
                        style={'width': '300px'}  # Adjust width as needed
                    ),
                ], className='mb-3'),  # Remove unnecessary flexbox and button div

                html.Button('Run Scenario', id='run-scenario-button', n_clicks=0, className='btn btn-dark ml-2 align-top'),  # Keep button separate

                dcc.Graph(id='scenario-data', className='mt-4')
            ], className='p-4 bg-light rounded')



# Callback to handle scenario analysis
@app.callback(
    Output('scenario-data', 'figure'),
    [Input('run-scenario-button', 'n_clicks')],
    [State('scenario-dropdown', 'value')]
)
def run_scenario_analysis(n_clicks, scenario):
    if n_clicks > 0:
        if scenario == 'base':
            scenario_data = data.copy()  # Base case, no change
        elif scenario == 'best':
            scenario_data = forecaster.generate_scenario(data, revenue_growth_rate=0.1, expense_change_factor=0.9)
        elif scenario == 'worst':
            scenario_data = forecaster.generate_scenario(data, revenue_growth_rate=-0.05, expense_change_factor=1.1)
        else:
            return {
                'data': [],
                'layout': {
                    'title': 'Scenario Analysis'
                }
            }

        return {
            'data': [
                {'x': scenario_data['date'], 'y': scenario_data['profit'], 'type': 'line', 'name': f'{scenario.capitalize()} Case Profit'}
            ],
            'layout': {
                'title': f'{scenario.capitalize()} Case Scenario Analysis'
            }
        }

    return {
        'data': [],
        'layout': {
            'title': 'Scenario Analysis'
        }
    }


# Callback to handle forecasting
@app.callback(
    Output('forecasted-data', 'figure'),
    [Input('forecast-button', 'n_clicks')],
    [State('date-picker-range', 'start_date'), State('date-picker-range', 'end_date')]
)
def update_forecast(n_clicks, start_date, end_date):
    if n_clicks > 0:
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            future_dates = pd.date_range(start=start_date, end=end_date, freq='MS').to_frame(index=False, name='date')
            predictions = forecaster.forecast(future_dates)
            future_dates['profit'] = predictions

            return {
                'data': [
                    {'x': future_dates['date'], 'y': future_dates['profit'], 'type': 'line', 'name': 'Forecasted Profit','line': {'color': 'red'}}
                ],
                'layout': {
                    'title': 'Forecasted Financial Data'
                }
            }
        except Exception as e:
            print(f"Error forecasting: {e}")

    return {
        'data': [],
        'layout': {
            'title': 'Forecasted Financial Data'
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
