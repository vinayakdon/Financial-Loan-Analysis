import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Loan Interactive EDA", layout="wide")


STATUS_COLORS = {
    "Fully Paid": "#2ecc71",
    "Charged Off": "#e74c3c",
    "Current": "#3498db"
}

CATEGORY_COLORS = px.colors.qualitative.Set2

#  LOAD DATA 
@st.cache_data
def load_data():
    df = pd.read_excel("financial_loan.xlsx")
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    df['issue_year'] = df['issue_date'].dt.year
    df['month_name'] = df['issue_date'].dt.strftime('%b')
    return df

df = load_data()

# SIDEBAR FILTERS
st.sidebar.title("🔍 Filters")

loan_status_filter = st.sidebar.multiselect(
    "Loan Status",
    df['loan_status'].unique(),
    df['loan_status'].unique()
)

year_filter = st.sidebar.multiselect(
    "Issue Year",
    sorted(df['issue_year'].unique()),
    sorted(df['issue_year'].unique())
)

df = df[
    (df['loan_status'].isin(loan_status_filter)) &
    (df['issue_year'].isin(year_filter))
]

st.title("🏦 Financial Loan Exploratory Data Analysis")

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Applications", f"{len(df):,}")
c2.metric("Total Loan Amount", f"${df['loan_amount'].sum()/1e6:.2f}M")
c3.metric("Total Amount Received", f"${df['total_payment'].sum()/1e6:.2f}M")
c4.metric("Avg Interest Rate", f"{df['int_rate'].mean()*100:.2f}%")

st.divider()

# LOAN STATUS 
loan_status_cnt = df.groupby('loan_status').size().reset_index(name='count')
fig = px.bar(
    loan_status_cnt,
    x='loan_status',
    y='count',
    color='loan_status',
    color_discrete_map=STATUS_COLORS,
    template="plotly_dark",
    title="Loan Status Distribution"
)
st.plotly_chart(fig, use_container_width=True)

# TOP PURPOSE 
top_purpose = df['purpose'].value_counts().head(5).reset_index()
top_purpose.columns = ['purpose', 'count']

fig = px.bar(
    top_purpose,
    x='count',
    y='purpose',
    color='purpose',
    color_discrete_sequence=CATEGORY_COLORS,
    template="plotly_dark",
    title="Top 5 Loan Purposes"
)
st.plotly_chart(fig, use_container_width=True)

# TOP STATES
state_vol = df.groupby('address_state')['loan_amount'].sum().nlargest(10).reset_index()

fig = px.bar(
    state_vol,
    x='address_state',
    y='loan_amount',
    color='loan_amount',
    color_continuous_scale="Blues",
    template="plotly_dark",
    title="Top 10 States by Total Loan Amount"
)
st.plotly_chart(fig, use_container_width=True)

#INT RATE VS GRADE
fig = px.box(
    df,
    x='grade',
    y='int_rate',
    color='grade',
    template="plotly_dark",
    title="Interest Rate vs Loan Grade"
)
st.plotly_chart(fig, use_container_width=True)

# CORRELATION
num_cols = ['annual_income', 'dti', 'installment', 'int_rate', 'loan_amount']
fig = px.imshow(
    df[num_cols].corr(),
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    template="plotly_dark",
    title="Correlation Heatmap"
)
st.plotly_chart(fig, use_container_width=True)

# MONTHLY FUNDED 
monthly_funded = (
    df.sort_values('issue_date')
    .assign(month=lambda x: x['issue_date'].dt.strftime('%b %Y'))
    .groupby('month')['loan_amount']
    .sum()
    .div(1_000_000)
    .reset_index()
)

fig = px.area(
    monthly_funded,
    x='month',
    y='loan_amount',
    template="plotly_dark",
    title="Monthly Funded Amount (Millions)"
)
fig.update_traces(line_color="#00c6ff", fillcolor="rgba(0,198,255,0.35)")
st.plotly_chart(fig, use_container_width=True)

# MONTHLY RECEIVED 
monthly_received = (
    df.sort_values('issue_date')
    .assign(month=lambda x: x['issue_date'].dt.strftime('%b %Y'))
    .groupby('month')['total_payment']
    .sum()
    .div(1_000_000)
    .reset_index()
)

fig = px.area(
    monthly_received,
    x='month',
    y='total_payment',
    template="plotly_dark",
    title="Monthly Amount Received (Millions)"
)
fig.update_traces(line_color="#2ecc71", fillcolor="rgba(46,204,113,0.35)")
st.plotly_chart(fig, use_container_width=True)

# Monthly Loan Applications (2021)
df_2021 = df[df['issue_year'] == 2021]
monthly_2021 = (
    df_2021.groupby('month_name')['loan_amount']
    .count()
    .reindex(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    .reset_index()
)

fig = px.line(
    monthly_2021,
    x='month_name',
    y='loan_amount',
    markers=True,
    line_shape="spline",
    color_discrete_sequence=["#f39c12"],
    title="Monthly Loan Applications (2021)",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# INCOME DISTRIBUTION

fig = px.histogram(
    df[df['annual_income'] < 150000],
    x='annual_income',
    nbins=40,
    color_discrete_sequence=["#8e44ad"],
    title="Distribution of Annual Income (<150k)",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)


# INCOME VS LOAN
fig = px.scatter(
    df[df['annual_income'] < 200000],
    x='annual_income',
    y='loan_amount',
    opacity=0.3,
    color_discrete_sequence=["#2ecc71"],
    title="Annual Income vs Loan Amount",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)

# Home Ownership Distribution

home_cnt = df['home_ownership'].value_counts().reset_index()
home_cnt.columns = ['home_ownership', 'count']

fig = px.pie(
    home_cnt,
    names='home_ownership',
    values='count',
    hole=0.6,
    color_discrete_sequence=px.colors.qualitative.Set3,
    title="Home Ownership Distribution",
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)


