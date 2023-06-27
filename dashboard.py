# --*-- coding: utf-8 --*--
"""
Created on Fri Jun 23 12:56:40 2023

@author: Saurabh Joshi
"""
import os

from alpha_vantage.fundamentaldata import FundamentalData
import plotly.graph_objects as go
from stocknews import StockNews
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

load_dotenv()

# Cred
AV_KEY = os.environ.get('AV_KEY')

# set streamlit web-app title
st.title('Stock Dashboard')

# ticker list
tickers = ('TSLA', 'AAPL', 'MSFT', 'F', 'AMZN')

ticker = st.selectbox(
    'Pick your Ticker',
    tickers
)

# Start and End date
col1, col2 = st.columns(2)

start = col1.date_input(
    'Start Date',
    value=pd.to_datetime('2023-01-01')
)

end = col2.date_input(
    'End Date',
    value=pd.to_datetime('today')
)

# Request data from yfinance
if len(ticker) > 0:
    # Get data from yfinance
    df = yf.download(ticker, start=start, end=end)
    # CandleStick chart
    st.subheader('Candle Stick Chart')
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )
        ]
    )
    st.plotly_chart(fig)

    # Line chart
    st.subheader('Adj Close Chart')
    fig = px.line(
        df,
        x=df.index,
        y = df['Adj Close']
    )
    st.plotly_chart(fig)

pricing_data, fundamental_data, news = st.tabs([
    'Pricing Data',
    'Fundamental Data',
    'Top 10 News'
])

with pricing_data:
    st.subheader('Price Movements')
    df['% Change'] = df['Adj Close'] / df['Adj Close'].shift(1) - 1
    st.write(df)

    # Get annual return for the % Change
    annual_return = df['% Change'].mean() * 252 * 100
    st.write(f'Annual Return is {round(annual_return, 2)}%')

    # Get annual SD for the % Change 
    stdev = np.std(df['% Change']) * np.sqrt(252)
    st.write(f'Annual Standard Deviation is {round(stdev * 100, 2)}%')

    # Get risk Adj. return
    st.write(f'Risk Adj Return is {round(annual_return / (stdev * 100), 2)}')

with fundamental_data:
    try:
        fd = FundamentalData(AV_KEY, output_format = 'pandas')
        # Balance Sheet
        st.subheader('Balance Sheet')
        raw_balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        balance_sheet = raw_balance_sheet.T[2:]
        balance_sheet.columns = list(raw_balance_sheet.T.iloc[0])
        st.write(balance_sheet)

        # Income Statement
        st.subheader('Income Statement')
        raw_income_statement = fd.get_income_statement_annual(ticker)[0]
        income_statement = raw_income_statement.T[2:]
        income_statement.columns = list(raw_income_statement.T.iloc[0])
        st.write(income_statement)

        # Cash Flow Statement
        st.subheader('CashFlow Statement')
        raw_cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cash_flow = raw_cash_flow.T[2:]
        cash_flow.columns = list(raw_cash_flow.T.iloc[0])
        st.write(cash_flow)

    except Exception as error:
        st.write(f'Error Occured!! Reached API limit')
        st.write(error)

with news:
    st.header(f'News of {ticker}')
    raw_stock_news = StockNews(ticker, save_news=False)
    df_news = raw_stock_news.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        st.write(f"Title Sentiment: {df_news['sentiment_title'][i]}")
        st.write(f"News Sentiment{df_news['sentiment_summary'][i]}")
