import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import numpy as np
from plotly.subplots import make_subplots
import math

# 데이터 로딩
@st.cache_data
def load_data():
    SEOUL_PUBLIC_API = st.secrets["api_credentials"]["SEOUL_PUBLIC_API"]

    # csv파일 불러오기
    data = pd.read_csv('data/data.csv', index_col=0)

    # 결측치 처리
    data = data.dropna(subset=['BUILD_YEAR'])

    # 거래일자 년월 추출
    data['datetime'] = pd.to_datetime(data['DEAL_YMD'], format="%Y%m%d")
    data['deal_year'] = data['datetime'].dt.year
    data['deal_month'] = data['datetime'].dt.month

    return data

@st.cache_data
def load_data2():
    rent = pd.read_csv("data/rent.csv", index_col=0)
    rent['datetime'] = pd.to_datetime(rent['계약일'], format="%Y%m%d")
    rent['년'] = rent['datetime'].dt.year
    rent['월'] = rent['datetime'].dt.month
    return rent

def main():
    df = load_data()
    rent = load_data2()

    # st.data_editor(result)
    # 대시보드 메뉴
    with st.sidebar:
        selected = option_menu("Navigation", ["Home", "탐색적 자료분석", "Project Planning"],
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

    # 전월세 데이터 필터
    rent_sgg = rent.loc[rent['자치구명'] == SGG_NM, :]
    rent_mon = rent_sgg.loc[rent_sgg['월'] == deal_month, :]

    # mean_price = round(month_select['OBJ_AMT'].mean(), 2)
    mean_price = math.ceil(month_select['OBJ_AMT'].mean())

    # ttl_count = sgg_select.loc[sgg_select['deal_year'] == deal_year].shape[0]
    ttl_count = month_select.shape[0]

    # 선택된 메뉴에 따라 다른내용 표시
    if selected == "Home":
        st.header("[Seoul] Real-Estate DashBoard")
        st.divider()
        st.subheader(str(SGG_NM) + " " + str(deal_year) + "년 " + str(deal_month) + "월 아파트 가격 개요")
        st.write("자치구와 년, 월을 클릭하면 자동으로 각 지역구의 평균 매매가, 총 거래량, 거래된 최소가격, 최대가격을 확인할 수 있습니다.")
        st.write("")

        # KPI
        kpi1, kpi2 = st.columns(2)   
        kpi1.metric(
        label = SGG_NM + " 평균 매매가 (만원) ⏳",
        value = '{:,}'.format(mean_price)
        # delta='{:,}'.format((mean_2024 - mean_2023).round(2))
        )

        kpi2.metric(
            label= SGG_NM + " 총 거래량 💍",
            value='{:,}'.format(ttl_count),
            # delta= count_2024 - count_2023
        )

        kpi3, kpi4 = st.columns(2)   
        kpi1.metric(
            label = SGG_NM + " 최소 매매가⬇️",
            value = '{:,}'.format(house1['OBJ_AMT'].min())
            # delta='{:,}'.format((mean_2024 - mean_2023).round(2))
            )

        kpi2.metric(
            label= SGG_NM + " 최대 매매가⬆️",
            value='{:,}'.format(house1['OBJ_AMT'].max()),
            # delta= count_2024 - count_2023
        )
        st.divider()

        # top10_apt = house1.groupby('BLDG_NM')['OBJ_AMT'].mean().astype(int).sort_values(ascending=False).reset_index(drop=False).head(10)
        # bottom10_apt = house1.groupby('BLDG_NM')['OBJ_AMT'].mean().astype(int).sort_values().reset_index(drop=False).head(10)

        # top10_apt = house1.groupby('BLDG_NM').agg({
        #     'SGG_NM': 'first',  # assuming 'SGG_NM' is the same for each group
        #     'BJDONG_NM': lambda x: list(set(x))[0],  # get a list of distinct 'BJDONG_NM' values for each group
        #     'OBJ_AMT': 'mean'
        # }).astype({'OBJ_AMT': int}).sort_values(by='OBJ_AMT', ascending=False).head(10).reset_index(drop=False)

        top10_apt = house1.sort_values(by='OBJ_AMT', ascending=False).head(10).reset_index(drop=False)
        top10_apt = top10_apt[['SGG_NM', 'BJDONG_NM', 'BLDG_NM', 'OBJ_AMT']]
        
        bottom10_apt = house1.sort_values(by='OBJ_AMT').head(10).reset_index(drop=False)
        bottom10_apt = bottom10_apt[['SGG_NM', 'BJDONG_NM', 'BLDG_NM', 'OBJ_AMT']]

        # Format 'OBJ_AMT' column with commas
        top10_apt['OBJ_AMT'] = top10_apt['OBJ_AMT'].apply(lambda x: "{:,}".format(x))
        bottom10_apt['OBJ_AMT'] = bottom10_apt['OBJ_AMT'].apply(lambda x: "{:,}".format(x))

        st.subheader("Top 10 Apartments🌿")
        st.dataframe(top10_apt, 
                    column_config={
                        'SGG_NM': '자치구',
                        'BJDONG_NM': '법정동',
                        'BLDG_NM':'아파트명', 
                        'OBJ_AMT':'건물가격'
                        },
                    width=600, height=390
                    )
        
        st.divider()
            
        st.subheader("Lowest 10 Apartments🍁")
        st.dataframe(bottom10_apt, 
                    column_config={
                        'SGG_NM': '자치구',
                        'BJDONG_NM': '법정동',
                        'BLDG_NM':'아파트명', 
                        'OBJ_AMT':'건물가격'},
                    width=600, height=390)

    elif selected == "탐색적 자료분석":
        st.header("Overview to EDA")
        tab1, tab2, tab3 = st.tabs(['Home', 'Visualization 1.', 'Visualization 2.'])

        with tab1: # Home
            st.subheader("Visualization 1.")
            st.write("- 주거유형 별 매매 비율")
            st.write("- 전월세 비율")

            st.subheader("Visualization 2.")
            st.write("- 지역별 평균 가격 막대 그래프")
            st.write("- 주거형태별 평균 가격 추세")
            st.write("- 주거형태별 거래 건수 추세")

        with tab2:
            # st.subheader("주거유형 별 매매 비율")
            fig = px.pie(month_select, values='OBJ_AMT', names='HOUSE_TYPE', title='주거유형 별 매매 비율')
            st.plotly_chart(fig)

            # st.subheader("전월세 비율")
            fig = px.pie(rent_mon, values='계약일', names='전월세구분', title='자치구별 전월세 비율',
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig)

            # 임대료 증감률
            rent_mon = rent.loc[rent['월'] == deal_month, :]
            rent_mon['임대료증감'] = rent_mon['임대료(만원)'] - rent_mon['종전임대료']
            rent_mon['보증금증감'] = rent_mon['보증금(만원)'] - rent_mon['종전보증금']

            fig = px.bar(rent_mon, x='자치구명', y='임대료증감', 
                         title='자치구별 임대료 증감률', color_discrete_sequence=['#5050FF'])
            
            fig.update_yaxes(showticklabels=False)
            fig.update_layout(xaxis_title='', yaxis_title="")
            st.plotly_chart(fig)

            # 보증금 증감률
            fig = px.bar(rent_mon, x='자치구명', y='보증금증감', title='자치구별 보증금 증감률')
            fig.update_yaxes(showticklabels=False)
            fig.update_layout(xaxis_title='', yaxis_title="")
            st.plotly_chart(fig)

        with tab3:
            with st.sidebar:
                chart_select = st.radio('차트 메뉴', [
                    '지역별 평균 가격 막대 그래프', '주거형태별 평균 가격 추세', '주거형태별 거래 건수 추세'
                    ])

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
                house_sel = st.radio('주거 유형을 선택하세요', ['아파트', '오피스텔', '연립다세대', '단독다가구'])

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

            elif chart_select == "주거형태별 평균 가격 추세":
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

            elif chart_select == "주거형태별 거래 건수 추세":
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


    # fig = px.histogram(sgg_select, x='BUILD_YEAR',
    #                 title='서울시 각 구별 건축연도 분포',
    #                 labels={'BUILD_YEAR': '건축연도', 'count': '건물 수'})
    # fig.update_xaxes(range=[2000, 2023])

    # st.plotly_chart(fig)

    # fig = px.density_heatmap(sgg_select, x='BUILD_YEAR', 
    #                 title='서울시 각 구별 건축연도 분포',
    #                 labels={'BUILD_YEAR': '건축연도', 'count': '건물 수'}, nbinsx=30, nbinsy=30)

    # fig.update_xaxes(range=[2000, 2023])

    # 그래프 출력
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=sgg_select['BLDG_AREA'], y=sgg_select['OBJ_AMT'], mode='markers', name='아파트'))
                
    # st.plotly_chart(fig)

    
    # st.write(SGG_NM)
    # st.data_editor(df.loc[df['SGG_NM'] == SGG_NM, :])




if __name__ == "__main__":
    main()

