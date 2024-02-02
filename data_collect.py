# data_collect.py
import streamlit as st 
import pandas as pd 
import requests 
import json 
import pandas as pd 

@st.cache_data
def load_data():
    SEOUL_PUBLIC_API = st.secrets["api_credentials"]["SEOUL_PUBLIC_API"]
    st.write(SEOUL_PUBLIC_API)
    URL = f'http://openapi.seoul.go.kr:8088/{SEOUL_PUBLIC_API}/json/tbLnOpendataRtmsV/1/100/'
    st.write(URL)
    content = requests.get(URL).json()
    data = pd.DataFrame(content['tbLnOpendataRtmsV']['row'])
    return data