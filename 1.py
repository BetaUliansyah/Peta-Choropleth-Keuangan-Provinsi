# Data Source: https://public.tableau.com/app/profile/federal.trade.commission/viz/FraudandIDTheftMaps/AllReportsbyState
# US State Boundaries: https://public.opendatasoft.com/explore/dataset/us-state-boundaries/export/

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = 'Peta Keuangan Provinsi di Indonesia'
APP_SUB_TITLE = 'Source: BPS, BIG, DJPK'

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    #Load Data
    df_ipm = pd.read_csv('ipm-provinsi-2024.csv')
    
    #Display Filters and Map
    year, quarter = display_time_filters(df_continental)
    state_name = display_map(df_continental, year, quarter)
    state_name = display_state_filter(df_continental, state_name)
    report_type = display_report_type_filter()

    #Display Metrics
    st.subheader(f'{state_name} {report_type} Facts')

    col1, col2, col3 = st.columns(3)
    with col1:
        display_fraud_facts(df_fraud, year, quarter, report_type, state_name, 'State Fraud/Other Count', f'# of {report_type} Reports', string_format='{:,}')
    with col2:
        display_fraud_facts(df_median, year, quarter, report_type, state_name, 'Overall Median Losses Qtr', 'Median $ Loss', is_median=True)
    with col3:
        display_fraud_facts(df_loss, year, quarter, report_type, state_name, 'Total Losses', 'Total $ Loss')        


if __name__ == "__main__":
    main()