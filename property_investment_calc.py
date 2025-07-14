import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Property Investment Financial Calculator")

# Default values
property_price = st.number_input("Property Price (INR)", value=1_00_00_000, step=100000)
down_payment_pct = st.slider("Down Payment (%)", 10, 100, 25)
loan_interest = st.slider("Loan Interest Rate (%)", 5.0, 15.0, 9.0)
loan_years = st.slider("Loan Tenure (years)", 1, 30, 20)
rental_income = st.number_input("Monthly Rental Income (INR)", value=25_000, step=1000)
rental_appreciation = st.slider("Rental Appreciation (%) every 2 years", 0, 20, 10)
property_appreciation = st.slider("Property Value Appreciation (%) per year", 0, 20, 5)
holding_years = st.slider("Holding Period (years)", 1, 30, 10)
disposal_cost_pct = st.slider("Disposal Cost (%)", 0, 10, 2)

# Calculations
down_payment = property_price * down_payment_pct / 100
loan_amount = property_price - down_payment
monthly_interest = loan_interest / 12 / 100
num_payments = loan_years * 12

# EMI calculation
emi = loan_amount * monthly_interest * (1 + monthly_interest) ** num_payments / ((1 + monthly_interest) ** num_payments - 1)

# Prepare year-wise breakdown
data = []
total_invested = down_payment
total_rent = 0
loan_balance = loan_amount
cumulative_cashflow = -down_payment
breakeven_year = None

for year in range(1, holding_years + 1):
    # Rental income for the year
    rent_this_year = rental_income * 12 * (1 + rental_appreciation / 100) ** ((year - 1) // 2)
    total_rent += rent_this_year

    # Loan payment for the year
    interest_paid = 0
    principal_paid = 0
    for m in range(12):
        interest = loan_balance * monthly_interest
        principal = emi - interest
        loan_balance -= principal
        interest_paid += interest
        principal_paid += principal
        if loan_balance < 0:
            loan_balance = 0
            break

    # Property value appreciation
    property_value = property_price * (1 + property_appreciation / 100) ** year

    # Cashflow
    cashflow = rent_this_year - emi * 12
    cumulative_cashflow += cashflow

    # Net worth if sold
    disposal_cost = property_value * disposal_cost_pct / 100
    net_sale = property_value - disposal_cost - loan_balance
    net_profit = net_sale + cumulative_cashflow

    # Breakeven check
    if breakeven_year is None and net_profit >= 0:
        breakeven_year = year

    data.append({
        "Year": year,
        "Property Value": round(property_value, 0),
        "Loan Balance": round(loan_balance, 0),
        "Total Rent": round(total_rent, 0),
        "Interest Paid": round(interest_paid, 0),
        "Principal Paid": round(principal_paid, 0),
        "Cumulative Cashflow": round(cumulative_cashflow, 0),
        "Net Profit (if sold)": round(net_profit, 0),
    })

df = pd.DataFrame(data)

st.subheader("Year-wise Investment Breakdown")
st.dataframe(df)

st.subheader("Investment & Returns Over Time")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["Property Value"], label="Property Value")
ax.plot(df["Year"], df["Loan Balance"], label="Loan Balance")
ax.plot(df["Year"], df["Cumulative Cashflow"], label="Cumulative Cashflow")
ax.plot(df["Year"], df["Net Profit (if sold)"], label="Net Profit (if sold)")
ax.set_xlabel("Year")
ax.set_ylabel("INR")
ax.legend()
st.pyplot(fig)

if breakeven_year:
    st.success(f"Breakeven achieved in year {breakeven_year}!")
else:
    st.info("Breakeven not achieved within holding period.")

st.caption("All values are approximate and for illustration only.")