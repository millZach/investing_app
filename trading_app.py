import streamlit as st
import trading_functions as tf
from datetime import date, timedelta

st.title("AnalytIQ")
page_select = st.sidebar.selectbox(
    'Pages',
    ('Targeted Volitility', 'SPY SMA', 'About')
)

if page_select == 'Targeted Volitility':
    st.markdown('''
        This page utilizes a trading strategy based on the month to month volitlity
        of a 3x Levereged ETF (Exchange-Traded Fund) paired with a bond. The allocation will be based on
        the user's acceptable amount of risk. More risk equals more reward, but also
        larger downside.
        ''')

    etf = st.sidebar.text_input('ETF Ticker', 'TQQQ').upper()
    bond = st.sidebar.text_input('Bond Ticker', 'TMF').upper()
    tickers = [etf, bond]
    target_vol_input = st.sidebar.number_input(
        'Target Volitility (%)',
        value=25,
        min_value=1,
        max_value=100,
    )
    target_vol = target_vol_input / 100
    start_date = st.sidebar.date_input(
        'Start Date',
        date.today() - timedelta(days=30)
    )
    end_date = st.sidebar.date_input('End Date')

    analyze = st.button('Run Analysis')
    if analyze:
        # Grabs data for stocks based on user specifications
        stock_dict = tf.stock_data_grab(tickers, start_date, end_date)
        # Calculates returns
        stock_dict_ret = tf.returns(stock_dict)
        # Calculates key statistics
        stock_df_merged, stats_df, stats_dict, view_stats = tf.key_statistics(
            stock_dict_ret, target_vol, bond)

        tf.allocation_pie_chart(stats_dict, tickers)
        st.pyplot()
        tf.correlation_heat_map(stock_df_merged)
        st.pyplot()
        st.write(view_stats)

if page_select == 'SPY SMA':
    st.markdown('''
        This shows the simple moving average (SMA) for the S&P 500, based on a user set window, ie. 200 day, 100 day
        etc. The dates for analysis can be set by the user in the sidebar, as well as, the SMA window.
        ''')

    start_date = st.sidebar.date_input(
        'Start Date',
        date.today() - timedelta(days=365)
    )
    end_date = st.sidebar.date_input('End Date')

    window = st.sidebar.selectbox('SMA Window (days)', (200, 150, 100, 50))

    tf.plot_200ma(start_date, end_date, window)
    st.pyplot()

if page_select == 'About':
    st.markdown(
        '''
        **Strategy Development:** Drake Morey

        **Site Development:** Zachery Miller

        **Contact Email:** zachknudsen@ymail.com

        This strategy utilized for this site is based on month to month volitlity of
        a 3x levereged ETF (Exchange-Traded Fund), which is paired with a non-correlated
        bond.

        The purpose of this site is for educational and infomational purposes only.
        Nothing contained on this site should be constructed as an invitation or
        solicitation to buy or sell any security.
        '''
    )
