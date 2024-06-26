def calculate_profitability_ratios(data):
    data['profit_margin'] = data['profit'] / data['revenue']
    data['return_on_assets'] = data['profit'] / (data['revenue'] + data['expenses'])
    data['return_on_equity'] = data['profit'] / (data['revenue'] - data['expenses'])
    return data

def calculate_liquidity_ratios(data):
    data['current_ratio'] = (data['revenue'] + data['expenses']) / data['expenses']
    data['quick_ratio'] = (data['revenue'] - data['expenses']) / data['expenses']
    return data

def calculate_leverage_ratios(data):
    data['debt_to_equity_ratio'] = data['expenses'] / data['profit']
    data['interest_coverage_ratio'] = data['revenue'] / data['expenses']
    return data
