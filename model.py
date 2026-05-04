import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# =========================
# STEP 1: Load Dataset
# =========================
df = pd.read_csv(
    "data/dataset.csv",
    skiprows=4,
    encoding='latin1',
    on_bad_lines='skip'
)

# =========================
# STEP 2: Filter India
# =========================
df = df[df['Country Name'] == 'India']

# =========================
# STEP 3: Drop unnecessary columns
# =========================
df = df.drop(columns=[
    'Country Name',
    'Country Code',
    'Indicator Name',
    'Indicator Code'
])

# =========================
# STEP 4: Convert wide → long
# =========================
df = df.melt(var_name='Year', value_name='Inflation')

# =========================
# STEP 5: Clean data
# =========================
df = df.dropna()
df['Year'] = df['Year'].astype(int)
df = df.sort_values('Year')

print("Cleaned Data:")
print(df.head())
print(df.tail())

# =========================
# STEP 6: Feature Engineering
# =========================
df['Lag1'] = df['Inflation'].shift(1)
df = df.dropna()

print("\nData with Lag Feature:")
print(df.head())

# =========================
# STEP 7: Train Model
# =========================
X = df[['Lag1']]
y = df['Inflation']

model = LinearRegression()
model.fit(X, y)

print("\nModel trained successfully")

# =========================
# STEP 8: Prediction
# =========================
last_value = df['Inflation'].iloc[-1]

prediction = model.predict(
    pd.DataFrame([[last_value]], columns=['Lag1'])
)

print("\nNext Year Inflation Prediction:", round(prediction[0], 2), "%")

# =========================
# STEP 9: Visualization
# =========================
plt.figure()
plt.plot(df['Year'], df['Inflation'], label="Actual Inflation")
plt.xlabel("Year")
plt.ylabel("Inflation")
plt.title("Inflation Trend (India)")
plt.legend()
plt.show()