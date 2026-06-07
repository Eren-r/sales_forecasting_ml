import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


data = pd.read_csv('retail_sales_dataset.csv')

print(data.head())

data['Date'] = pd.to_datetime(data['Date'])

# Create daily aggregated sales 
if 'Sales' in data.columns:
    daily_sales = data.groupby('Date')['Sales'].sum().reset_index()
else:
    #total sales per row 
    data['TotalSales'] = data['Quantity'] * data['Price per Unit']
    daily_sales = data.groupby('Date')['TotalSales'].sum().reset_index()
    daily_sales.rename(columns={'TotalSales': 'Sales'}, inplace=True)


daily_sales = daily_sales.sort_values('Date')

# Visualize sales trend
plt.figure(figsize=(12,6))
plt.plot(daily_sales['Date'], daily_sales['Sales'], color='blue', label='Daily Sales')
plt.title('Daily Sales Over Time')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# create lagged sales features for past 3 days
def create_lagged_features(df, lag=3):
    df = df.copy()
    for i in range(1, lag+1):
        df[f'lag_{i}'] = df['Sales'].shift(i)
    df = df.dropna()
    return df

sales_lagged = create_lagged_features(daily_sales, lag=3)

X = sales_lagged[['lag_1', 'lag_2', 'lag_3']]
y = sales_lagged['Sales']

# training and test sets (80-20 split, no shuffle for time-series)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = LinearRegression()
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate model performance
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f'Root Mean Squared Error (RMSE): {rmse:.2f}')
print(f'R^2 Score: {r2:.2%}')

# Visualize actual vs predicted sales
plt.figure(figsize=(12,6))
plt.plot(y_test.values, label='Actual Sales', color='blue')
plt.plot(y_pred, label='Predicted Sales', color='orange')
plt.title('Actual vs Predicted Sales')
plt.xlabel('Days')
plt.ylabel('Sales')
plt.legend()
plt.tight_layout()
plt.show()
