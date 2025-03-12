import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="COVID Tracker",
    page_icon="🦠",
    layout="wide"
)

DATA_URL = "data.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    data["dateRep"] = pd.to_datetime(data["dateRep"], format="%d/%m/%Y")
    return data

data = load_data()

st.title("COVID Tracker 🦠")
st.markdown("👋 **Welcome!** This app tracks the evolution of COVID-19 cases worldwide.")
st.markdown("Data source: [European Centre for Disease Prevention and Control (ECDC)](https://www.ecdc.europa.eu/en/publications-data/data-daily-new-cases-covid-19-eueea-country)")

if st.checkbox('Show raw data'):
    st.subheader('Raw Data')
    st.write(data)

# =============================
# 🌍 COVID CASE ANALYSIS IN EUROPE
# =============================

st.header("📊 COVID Cases in Europe")
total_cases_by_country = data.groupby("countriesAndTerritories", as_index=False)["cases"].sum()
iso_mapping = data[["countriesAndTerritories", "countryterritoryCode"]].drop_duplicates()
total_cases_by_country = total_cases_by_country.merge(iso_mapping, on="countriesAndTerritories", how="left")

fig = px.choropleth(
    total_cases_by_country,
    locations="countryterritoryCode",
    color="cases",
    hover_name="countriesAndTerritories",
    color_continuous_scale="Reds",
    projection="orthographic",
    title="Total COVID Cases in Europe",
)

fig.update_geos(
    center={"lat": 54, "lon": 10},
    projection_scale=3.5,
    showcoastlines=True,
    showocean=True,
    oceancolor="lightblue",
    landcolor="white",
)

fig.update_layout(
    width=900,  
    height=650,  
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Total Cases"),
)

st.plotly_chart(fig, use_container_width=False)

st.subheader("📈 Daily COVID Cases in Europe")
daily_cases = data.groupby("dateRep")[["cases"]].sum().reset_index()
fig = px.line(
    daily_cases, x="dateRep", y="cases",
    labels={"dateRep": "Date", "cases": "Daily Cases"},
    title="Daily New COVID Cases in Europe",
    markers=True
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Cases",
    showlegend=False,
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)
st.subheader("💀 COVID Cases vs Deaths by Country")
cases_deaths = data.groupby("countriesAndTerritories", as_index=False)[["cases", "deaths"]].sum()
fig = px.scatter(
    cases_deaths, x="cases", y="deaths",
    size="cases", color="cases",
    hover_name="countriesAndTerritories",
    title="COVID Cases vs Deaths by Country",
    log_x=True, log_y=True
)

fig.update_layout(
    xaxis_title="Total Cases (log scale)",
    yaxis_title="Total Deaths (log scale)",
    showlegend=False,
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Top 10 Countries with Most COVID Cases")
top_countries = total_cases_by_country.sort_values(by="cases", ascending=False).head(10)

fig = px.bar(
    top_countries, x="cases", y="countriesAndTerritories",
    orientation="h", color="cases",
    title="Top 10 Most Affected Countries",
    labels={"cases": "Total Cases", "countriesAndTerritories": "Country"},
)

fig.update_layout(
    xaxis_title="Total Cases",
    yaxis_title="",
    showlegend=False,
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)

st.header("🌍 Country-Specific Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Monthly Cases by Country")
    country = st.selectbox("Select a country", data["countriesAndTerritories"].sort_values().unique())
    country_cases = data[data["countriesAndTerritories"] == country].copy()
    country_cases["year_month"] = country_cases["dateRep"].dt.to_period("M").astype(str)
    country_cases = country_cases.sort_values(by="dateRep")

    fig = px.histogram(
        country_cases, x="year_month", y="cases",
        labels={"year_month": "Month", "cases": "Number of Cases"},
        title=f"COVID-19 Cases Trend in {country}"
    )

    fig.update_layout(
        bargap=0.2,
        xaxis_title="Months",
        yaxis_title="Number of Cases",
        xaxis=dict(type="category"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Average Cases in Selected Period")
    
    with st.form("average_cases_per_country"):
        country = st.selectbox("Select a country", data["countriesAndTerritories"].sort_values().unique())
        start_period = st.date_input("Start date")
        end_period = st.date_input("End date")
        submit = st.form_submit_button("Submit")

        if submit:
            avg_period_country_cases = data[data["countriesAndTerritories"] == country].copy()
            avg_period_country_cases["dateRep"] = pd.to_datetime(avg_period_country_cases["dateRep"], format="%d/%m/%Y")
            mask = (avg_period_country_cases["dateRep"] >= start_period) & (avg_period_country_cases["dateRep"] <= end_period)
            avg_cases = avg_period_country_cases.loc[mask, "cases"].mean()

            if np.isnan(avg_cases):
                st.warning("No data available for the selected period.")
            else:
                st.metric("Average COVID Cases in Selected Period", np.round(avg_cases, 2))

