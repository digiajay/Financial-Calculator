import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# --- Currency selection ---
currency_options = {"INR": "₹", "USD": "$", "EUR": "€"}
currency = st.selectbox("Currency", options=list(currency_options.keys()), index=0)
currency_symbol = currency_options[currency]

# --- Layout ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:   
    st.header("Investment Inputs")
    property_price = st.number_input(f"Property Price ({currency_symbol})", value=1_00_00_000, step=100000, format="%d")
    
    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        down_payment_pct = st.slider("Down Payment (%)", 10, 100, 25, key="dp_slider")
    with sub_col2:
        down_payment_pct_input = st.number_input("",min_value=10, max_value=100, value=down_payment_pct, key="dp_input")
        if down_payment_pct != down_payment_pct_input:
            down_payment_pct = down_payment_pct_input
    
    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        loan_interest = st.slider("Loan Interest Rate (%)", 5.0, 15.0, 9.0, 0.01, key="li_slider")
    with sub_col2:
        loan_interest_input = st.number_input("", min_value=5.0, max_value=15.0, value=loan_interest, step=0.01, key="li_input")
    if loan_interest != loan_interest_input:
        loan_interest = loan_interest_input

    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        loan_years = st.slider("Loan Tenure (years)", 1, 50, 20, key="lt_slider")
    with sub_col2:
        loan_years_input = st.number_input("", min_value=1, max_value=50, value=loan_years, key="lt_input")
    if loan_years != loan_years_input:
        loan_years = loan_years_input

    
    rental_income = st.number_input(f"Monthly Rental Income ({currency_symbol})", value=25_000, step=1000, format="%d")
    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        rental_appreciation = st.slider("Rental Appreciation (%) every 2 years", 0, 20, 10, key="ra_slider")
    with sub_col2:
        rental_appreciation_input = st.number_input("", min_value=0, max_value=20, value=rental_appreciation, key="ra_input")
    if rental_appreciation != rental_appreciation_input:
        rental_appreciation = rental_appreciation_input
    
    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        property_appreciation = st.slider("Property Value Appreciation (%) per year", 0, 20, 5, key="pa_slider")
    with sub_col2:
        property_appreciation_input = st.number_input("", min_value=0, max_value=20, value=property_appreciation, key="pa_input")
    if property_appreciation != property_appreciation_input:
        property_appreciation = property_appreciation_input

    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        holding_years = st.slider("Holding Period (years)", 1, 50, 10, key="hy_slider")
    with sub_col2:
        holding_years_input = st.number_input("", min_value=1, max_value=50, value=holding_years, key="hy_input")
    if holding_years != holding_years_input:
        holding_years = holding_years_input

    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        disposal_cost_pct = st.slider("Disposal Cost (%)", 0, 10, 2, key="dc_slider")
    with sub_col2:
        disposal_cost_pct_input = st.number_input("", min_value=0, max_value=10, value=disposal_cost_pct, key="dc_input")
    if disposal_cost_pct != disposal_cost_pct_input:
        disposal_cost_pct = disposal_cost_pct_input

    st.header("Comparison Investment")
    sub_col1, sub_col2 = st.columns([3, 1], gap="large")
    with sub_col1:
        bank_interest_rate = st.slider("Bank/Bond Interest Rate (%)", 1.0, 15.0, 7.0, 0.1, key="bank_ir_slider")
    with sub_col2:
        bank_interest_rate_input = st.number_input("", min_value=1.0, max_value=15.0, value=bank_interest_rate, step=0.01, key="bank_ir_input")
    if bank_interest_rate != bank_interest_rate_input:
        bank_interest_rate = bank_interest_rate_input

# --- Calculations ---
down_payment = property_price * down_payment_pct / 100
loan_amount = property_price - down_payment
monthly_interest = loan_interest / 12 / 100
num_payments = loan_years * 12

# EMI calculation
if monthly_interest > 0:
    emi = loan_amount * monthly_interest * (1 + monthly_interest) ** num_payments / ((1 + monthly_interest) ** num_payments - 1)
else:
    emi = loan_amount / num_payments

# Prepare year-wise breakdown
data = []
total_rent = 0
loan_balance = loan_amount
cumulative_cashflow = -down_payment
breakeven_year = None
emi_active = True
cumulative_interest_paid = 0  # Add this before the loop

bank_balance = down_payment  # initial investment
bank_investments = [down_payment]  # list of all investments per year (for info)
bank_balance_history = []

for year in range(1, holding_years + 1):
    # Rental income for the year
    rent_this_year = rental_income * 12 * (1 + rental_appreciation / 100) ** ((year - 1) // 2)
    total_rent += rent_this_year

    # Loan payment for the year
    interest_paid = 0
    principal_paid = 0
    for m in range(12):
        if loan_balance > 0:
            interest = loan_balance * monthly_interest
            principal = emi - interest
            if principal > loan_balance:
                principal = loan_balance
                emi_payment = interest + principal
            else:
                emi_payment = emi
            loan_balance -= principal
            interest_paid += interest
            principal_paid += principal
        else:
            emi_active = False
            break

    # Property value appreciation
    property_value = property_price * (1 + property_appreciation / 100) ** year

    # Cashflow: after loan is paid, full rent is cashflow
    if emi_active:
        yearly_cashflow = rent_this_year - emi * 12
    else:
        yearly_cashflow = rent_this_year
    cumulative_cashflow += yearly_cashflow

    # Cumulative interest paid
    cumulative_interest_paid += interest_paid

    # Net worth if sold
    disposal_cost = property_value * disposal_cost_pct / 100
    net_sale = property_value - disposal_cost - loan_balance
    net_profit = net_sale + cumulative_cashflow

    # Breakeven check
    if breakeven_year is None and net_profit >= 0:
        breakeven_year = year

    # Bank/Bond investment value (compounded annually) for initial down payment only
    bank_investment_value = down_payment * (1 + bank_interest_rate / 100) ** year
    bank_investment_gain = bank_investment_value - down_payment

    # --- New: Simulate investing yearly negative cashflow in bank/bond ---
    # At the end of each year, invest the negative cashflow (if negative)
    if yearly_cashflow < 0:
        bank_balance += abs(yearly_cashflow)
        bank_investments.append(abs(yearly_cashflow))
    else:
        bank_investments.append(0)

    # Compound the entire bank balance for one year
    bank_balance = bank_balance * (1 + bank_interest_rate / 100)
    bank_balance_history.append(bank_balance)

    data.append({
        "Year": year,
        "Property Value": round(property_value, 0),
        "Loan Balance": round(loan_balance, 0),
        "Total Rent": round(total_rent, 0),
        "Interest Paid": round(interest_paid, 0),
        "Cumulative Interest Paid": round(cumulative_interest_paid, 0),
        "Principal Paid": round(principal_paid, 0),
        "Yearly Cashflow": round(yearly_cashflow, 0),
        "Cumulative Cashflow": round(cumulative_cashflow, 0),
        "Net Profit (if sold)": round(net_profit, 0),
        "Bank/Bond Value": round(bank_investment_value, 0),
        "Bank/Bond Gain": round(bank_investment_gain, 0),
        "Bank/Bond Value (With Cashflows)": round(bank_balance, 0),  # <-- new column
        "Bank/Bond Added This Year": round(bank_investments[-1], 0),  # <-- new column
    })
    #if year == 1:
    #    st.write(f"DEBUG: Down payment: {down_payment}, Rent: {rent_this_year}, EMI: {emi*12}, Cashflow: {cashflow}, Cumulative: {cumulative_cashflow}")

df = pd.DataFrame(data)

# --- Graph ---
with col2:
    st.header("Investment & Returns Over Time")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["Year"], df["Property Value"], label="Property Value")
    ax.plot(df["Year"], df["Loan Balance"], label="Loan Balance")
    ax.plot(df["Year"], df["Cumulative Cashflow"], label="Cumulative Cashflow")
    ax.plot(df["Year"], df["Net Profit (if sold)"], label="Net Profit (if sold)")
    ax.plot(df["Year"], df["Bank/Bond Value"], label="Bank/Bond Value", linestyle="--")
    ax.plot(df["Year"], df["Bank/Bond Value (With Cashflows)"], label="Bank/Bond Value (With Cashflows)", linestyle="--")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"{currency_symbol} (in Crores)")
    ax.legend()
    # Format y-axis in crores
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1e7:.7f}'))
    st.pyplot(fig)

    st.dataframe(df, use_container_width=True, height=400)

# --- Breakeven ---
if breakeven_year:
    st.success(f"Breakeven achieved in year {breakeven_year}!")
else:
    st.info("Breakeven not achieved within holding period.")

st.caption("All values are approximate and for illustration only.")