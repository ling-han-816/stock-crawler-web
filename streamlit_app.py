import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. 網頁配置與自定義 CSS 注入 (讓介面不單調的關鍵) ---
st.set_page_config(page_title="台股旗艦分析儀表板", layout="wide")

st.markdown("""
    <style>
    /* 調整主背景與文字顏色 */
    .main {
        background-color: #f8f9fa;
    }
    /* 讓標題更有設計感 */
    .main-title {
        font-size: 45px;
        font-weight: 800;
        color: #1E1E1E;
        text-align: center;
        margin-bottom: 20px;
        background: -webkit-linear-gradient(#2E3192, #1BFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* 美化資訊卡片 */
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 標題展示 ---
st.markdown('<p class="main-title">🚀 台股旗艦分析儀表板</p>', unsafe_allow_html=True)

# --- 2. 側邊欄優化 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=100) # 加上小圖示
    st.header("控制中心")
    stock_id = st.text_input("輸入股票代號", value="2330")
    st.info("💡 提示：輸入代碼後點擊下方按鈕開始全方位解析。")
    st.write("---")
    st.caption("⚡ Power by Streamlit & Gemini")

# --- 3. 功能邏輯 (Yahoo & News) ---
def get_yahoo_summary(sid):
    url = f'https://tw.stock.yahoo.com/quote/{sid}.TW'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        price = soup.find('span', class_='Fz(32px)').text
        change = soup.find('span', class_='Fz(20px)').text
        return price, change
    except:
        return "N/A", "N/A"

def get_cnyes_news(sid):
    url = f'https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={sid}&limit=8&page=1'
    try:
        items = requests.get(url).json()['data']['items']
        return items
    except:
        return []

# --- 4. 主要顯示區域 ---
if st.button("📊 執行全方位數據解析"):
    with st.spinner("正在對接全球數據庫..."):
        # 取得即時報價 (放在最上面最醒目的位置)
        price, change = get_yahoo_summary(stock_id)
        
        # 使用 Columns 製作「戰情室指標」
        #         col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("當前股價", f"{price} TWD", change)
        with col2:
            st.metric("分析標的", f"{stock_id}.TW")
        with col3:
            st.metric("數據來源", "即時串接")

        st.write("---")

        # 使用更美觀的 Tabs
        tab1, tab2, tab3 = st.tabs(["📈 趨勢分析", "🔍 詳細數據", "📰 深度新聞"])

        with tab1:
            st.subheader("Interactive Trend Chart")
            data = yf.download(f"{stock_id}.TW", period="1y")
            if not data.empty:
                # 繪
