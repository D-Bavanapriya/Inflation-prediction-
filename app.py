import streamlit as st
import pandas as pd

# =========================
# AI SETUP
# =========================
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# TITLE
# =========================
st.title("📊 Inflation Impact Analysis System")

# =========================
# LOAD DATASET
# =========================
df_raw = pd.read_csv(
    "data/dataset.csv",
    skiprows=4,
    encoding='latin1',
    on_bad_lines='skip'
)

df_raw = df_raw[df_raw['Country Name'] == 'India']

df_raw = df_raw.drop(columns=[
    'Country Name',
    'Country Code',
    'Indicator Name',
    'Indicator Code'
])

df_raw = df_raw.melt(var_name='Year', value_name='Inflation')
df_raw = df_raw.dropna()
df_raw['Year'] = df_raw['Year'].astype(int)

df_raw = df_raw.sort_values('Year')

# =========================
# FUTURE BASE YEAR
# =========================
current_year = 2026

# =========================
# RATE SELECTION
# =========================
st.subheader("📌 Select Inflation Rate Source")

option = st.radio(
    "Choose Rate Type",
    ["Manual Input", "Auto (Average from Data)"]
)

if option == "Manual Input":
    rate = st.number_input("Enter Inflation Rate (%)", value=7.0)
else:
    rate = df_raw['Inflation'].mean()
    st.write(f"📊 Average Inflation Rate (based on past data): {round(rate, 2)} %")

r = rate / 100

# =========================
# USER INPUTS
# =========================
amount = st.number_input("Enter Amount (₹)", value=2000)

target_year = st.number_input(
    "Enter Target Year (e.g., 2035)",
    min_value=current_year + 1,
    max_value=current_year + 50,
    value=current_year + 5
)

# =========================
# FUTURE YEARS GENERATION
# =========================
future_years = list(range(current_year, target_year + 1))

# =========================
# CATEGORY FACTORS
# =========================
gold_factor = 1.2
food_factor = 1.05
rent_factor = 1.08

# =========================
# CALCULATIONS
# =========================
data = []

for i, year_value in enumerate(future_years):
    t = i

    money = amount * ((1 - r) ** t)
    gold = amount * ((1 + r * gold_factor) ** t)
    food = amount * ((1 + r * food_factor) ** t)
    rent = amount * ((1 + r * rent_factor) ** t)

    data.append({
        "Year": year_value,
        "Money Value (₹)": round(money, 2),
        "Gold Price (₹)": round(gold, 2),
        "Food Cost (₹)": round(food, 2),
        "Rent Cost (₹)": round(rent, 2)
    })

df = pd.DataFrame(data)

# =========================
# OUTPUT TABLE
# =========================
st.subheader("📊 Inflation Impact Table (Future Projection)")
st.dataframe(df)

# =========================
# FINAL SUMMARY
# =========================
final = df.iloc[-1]

st.subheader(f"📌 Summary for Year {target_year}")

st.write(f"💰 Money Value: ₹{final['Money Value (₹)']}")
st.write(f"🪙 Gold Price: ₹{final['Gold Price (₹)']}")
st.write(f"🍚 Food Cost: ₹{final['Food Cost (₹)']}")
st.write(f"🏠 Rent Cost: ₹{final['Rent Cost (₹)']}")

# =========================
# INVESTMENT RECOMMENDATION
# =========================
st.subheader("💡 Investment Recommendation")

options = {
    "Gold": final["Gold Price (₹)"],
    "Food Sector": final["Food Cost (₹)"],
    "Real Estate (Rent)": final["Rent Cost (₹)"]
}

best_option = max(options, key=options.get)

st.success(f"📌 Suggested Investment: {best_option}")

st.write("Reason:")
if best_option == "Gold":
    st.write("Gold shows the highest growth under inflation and acts as a strong hedge.")
elif best_option == "Food Sector":
    st.write("Food demand remains constant, leading to steady price growth.")
else:
    st.write("Real estate benefits from long-term inflation and rental increases.")

# =========================
# AI INSIGHT SECTION
# =========================
st.subheader("🧠 AI Financial Insight")

if st.button("Generate AI Insight"):
    with st.spinner("Analyzing..."):
        prompt = f"""
        Inflation rate: {rate:.2f}%
        Initial amount: ₹{amount}
        Target year: {target_year}

        Final values:
        Money Value: ₹{final['Money Value (₹)']}
        Gold Price: ₹{final['Gold Price (₹)']}
        Food Cost: ₹{final['Food Cost (₹)']}
        Rent Cost: ₹{final['Rent Cost (₹)']}

        Suggested Investment: {best_option}

        Explain:
        1. Inflation impact on money
        2. Why gold/food/rent behave differently
        3. Why the suggested investment is best
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.success("✅ Insight Generated")
            st.write(response.choices[0].message.content)

        except Exception:
            st.error("⚠️ Error generating insight. Check API key or internet.")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("About")
st.sidebar.write(
    "This system projects inflation impact from 2026 onwards and analyzes "
    "how purchasing power and sectors like gold, food, and rent change over time. "
    "It also provides AI-based financial insights."
)