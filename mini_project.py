import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import numpy as np
from plotly.subplots import make_subplots

# 데이터 로딩
@st.cache_data
def load_data():
    SEOUL_PUBLIC_API = st.secrets["api_credentials"]["SEOUL_PUBLIC_API"]

    # csv파일 불러오기
    data = pd.read_csv('data.csv', index_col=0)

    # 결측치 처리
    data = data.dropna(subset=['BUILD_YEAR'])

    # 거래일자 년월 추출
    data['datetime'] = pd.to_datetime(data['DEAL_YMD'], format="%Y%m%d")
    data['deal_year'] = data['datetime'].dt.year
    data['deal_month'] = data['datetime'].dt.month
    return data

def main():
    df = load_data()
    # st.data_editor(result)
    # 대시보드 메뉴
    with st.sidebar:
        selected = option_menu("대시보드 메뉴", ["Home", "탐색적 자료분석", "Project Planning"],
                            icons=['house', 'bar-chart-steps', 'kanban'],
                            menu_icon="app-indicator", default_index=0,
                            styles={
            "container": {"padding": "5!important", "background-color": "#black"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
        )
        SGG_NM = st.selectbox("지역구를 선택하세요", sorted(list(df['SGG_NM'].unique())))
        deal_year = st.radio("년도를 선택하세요", sorted(list(df['deal_year'].unique())))

        unique_month = sorted(df[df['deal_year'] == deal_year]['deal_month'].unique())
        deal_month = st.selectbox("월을 선택하세요", unique_month)

    # 시군구, 연,월 필터
    sgg_select = df.loc[df['SGG_NM'] == SGG_NM, :]
    year_select = sgg_select.loc[sgg_select['deal_year'] == deal_year, :]
    month_select = year_select.loc[year_select['deal_month'] == deal_month, :]

    # 주거타입 필터
    house1 = month_select[month_select['HOUSE_TYPE']=='아파트']
    house2 = month_select[month_select['HOUSE_TYPE']=='오피스텔']
    house3 = month_select[month_select['HOUSE_TYPE']=='연립다세대']
    house4 = month_select[month_select['HOUSE_TYPE']=='단독다가구']

    # sgg_mean_price = sgg_select.loc[sgg_select['deal_year'] == deal_year]['OBJ_AMT'].mean().round(2)
    # sgg_mean_price = sgg_select['OBJ_AMT'].mean().round(2)
    mean_price = round(month_select['OBJ_AMT'].mean(), 2)

    # ttl_count = sgg_select.loc[sgg_select['deal_year'] == deal_year].shape[0]
    ttl_count = month_select.shape[0]

    # 선택된 메뉴에 따라 다른내용 표시
    if selected == "Home":
        st.header("대시보드 개요")
        st.divider()

        kpi1, kpi2 = st.columns(2)   

        kpi1.metric(
        label="평균 매매가 (만원) ⏳",
        value='{:,}'.format(mean_price)
        # delta='{:,}'.format((mean_2024 - mean_2023).round(2))
        )

        kpi2.metric(
            label="총 거래량 💍",
            value='{:,}'.format(ttl_count),
            # delta= count_2024 - count_2023
        )

    elif selected == "탐색적 자료분석":
        st.header("탐색적 자료분석 개요")
        tab1, tab2, tab3 = st.tabs(['Home', 'Visualization', 'Statistics'])

        with tab1: # Home
            st.subheader("Visualization 개요")
            st.write("- 지역별 평균 가격 막대 그래프")
            st.write("- 가구형태별 평균 가격 추세")
            st.write("- 가구형태별 거래 건수 추세")
            st.subheader("Statistics 개요")
    
        with tab2:
            with st.sidebar:
                chart_select = st.radio('차트 메뉴', ['지역별 평균 가격 막대 그래프', '가구형태별 평균 가격 추세', '가구형태별 거래 건수 추세'])

            if chart_select == "지역별 평균 가격 막대 그래프":
                st.subheader("지역별 평균 가격 막대 그래프")
                st.write("")
                
                # 연,월,주거타입 필터
                year_sel = df[df['deal_year'] == deal_year]
                month_sel = year_sel[year_sel['deal_month'] == deal_month]
                house1 = month_sel[month_sel['HOUSE_TYPE']=='아파트']
                house2 = month_sel[month_sel['HOUSE_TYPE']=='오피스텔']
                house3 = month_sel[month_sel['HOUSE_TYPE']=='연립다세대']
                house4 = month_sel[month_sel['HOUSE_TYPE']=='단독다가구']

                # 주거유형 선택 버튼
                house_sel = st.radio('가구 유형을 선택하세요', ['아파트', '오피스텔', '연립다세대', '단독다가구'])

                if house_sel == '아파트':
                    fig = px.bar(house1, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '오피스텔':
                    fig = px.bar(house2, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '연립다세대':
                    fig = px.bar(house3, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)
                elif house_sel == '단독다가구':
                    fig = px.bar(house4, x='SGG_NM', y='OBJ_AMT')
                    fig.update_layout(xaxis_title='', yaxis=dict(title_text='물건가격(만원)'))
                    st.plotly_chart(fig)   

            elif chart_select == "가구형태별 평균 가격 추세":
                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=house1['datetime'], y=house1['OBJ_AMT'], mode='lines+markers', name='아파트'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house2['datetime'], y=house2['OBJ_AMT'], mode='lines+markers', name="오피스텔"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=house3['datetime'], y=house3['OBJ_AMT'], mode='lines+markers', name='연립다세대'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=house4['datetime'], y=house4['OBJ_AMT'], mode='lines+markers', name='단독다가구'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                # dtick=50000, range=[0, 150000],
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='물건가격(만원)', row=2, col=2)

                fig.update_layout(width=1000, height=600)
                st.plotly_chart(fig)

            elif chart_select == "가구형태별 거래 건수 추세":
                cnt1 = house1.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt2 = house2.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt3 = house3.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")
                cnt4 = house4.groupby('datetime')['OBJ_AMT'].count().reset_index(name="counts")

                fig = make_subplots(rows=2, cols=2)
                fig.add_trace(
                    go.Scatter(x=cnt1['datetime'], y=cnt1['counts'], mode='lines+markers', name='아파트'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt2['datetime'], y=cnt2['counts'], mode='lines+markers', name="오피스텔"),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=cnt3['datetime'], y=cnt3['counts'], mode='lines+markers', name='연립다세대'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=cnt4['datetime'], y=cnt4['counts'], mode='lines+markers', name='단독다가구'),
                    row=2, col=2
                )

                fig.update_xaxes(showticklabels=False, row=1, col=1)
                fig.update_xaxes(showticklabels=False, row=1, col=2)
                fig.update_xaxes(showticklabels=False, row=2, col=1)
                fig.update_xaxes(showticklabels=False, row=2, col=2)

                # dtick=50000, range=[0, 150000],
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=1, col=1)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=1, col=2)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=2, col=1)
                fig.update_yaxes(tickformat=',', title_text='거래건수', row=2, col=2)

                fig.update_layout(width=800, height=500)
                st.plotly_chart(fig)

# 아파트 연립다세대 오피스텔 단독다가구
        # with tab3:


    # fig = px.histogram(df_select, x='BUILD_YEAR',
    #                 title='서울시 각 구별 건축연도 분포',
    #                 labels={'BUILD_YEAR': '건축연도', 'count': '건물 수'})
    # fig.update_xaxes(range=[1900, 2023])

    # st.plotly_chart(fig)

    # fig = px.density_heatmap(df_select, x='BUILD_YEAR', 
    #                 title='서울시 각 구별 건축연도 분포',
    #                 labels={'BUILD_YEAR': '건축연도', 'count': '건물 수'})

    # fig.update_xaxes(range=[1900, 2023])

    # 그래프 출력
    # st.plotly_chart(fig)

    
    st.write(SGG_NM)

    st.data_editor(df.loc[df['SGG_NM'] == SGG_NM, :])




if __name__ == "__main__":
    main()

