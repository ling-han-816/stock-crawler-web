import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import datetime as dt
from bs4 import BeautifulSoup
from datetime import datetime

# --- 網頁頁面配置與標題 (美化重點 1) ---
st.set_page_config(page_title="台股分析網頁", layout="wide")
# st.title("📈 我的台股全方位分析系統")

# --- 側邊欄輸入區 (美化重點 2) ---
with st.sidebar:
    st.header("🔍 查詢設定")
    # 對輸入框加上更清晰的提示
    stock_id = st.text_input("請輸入台股代號", value="2330")
    st.write("---")
    st.write("**資料來源**")
    st.caption("整合：證交所、Yahoo 股市、鉅亨網、yfinance")

# --- 定義功能函式 (這部分原本邏輯不變) ---
def get_yahoo_data(sid):
    url = f'https://tw.stock.yahoo.com/quote/{sid}.TW'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    info_section = soup.find('section', {'id': 'qsp-overview-realtime-info'})
    if not info_section: return None
    fields, datas = [], []
    for item in info_section.find_all('li'):
        spans = item.find_all('span')
        if len(spans) >= 2:
            fields.append(spans[0].text.strip())
            datas.append(spans[1].text.strip())
    return pd.DataFrame([datas], columns=fields)

def get_cnyes_news(sid):
    url = f'https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={sid}&limit=10&page=1'
    try:
        json_data = requests.get(url).json()
        items = json_data['data']['items']
        data = []
        for item in items:
            pub_date = datetime.fromtimestamp(item["publishAt"]).strftime('%Y-%m-%d')
            data.append({"日期": pub_date, "標題": item["title"], "連結": f'https://news.cnyes.com/news/id/{item["newsId"]}'})
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# --- 按鈕觸發與結果顯示區 ---
if st.button("🚀 開始執行全方位分析"):
    
    # 加上 Spinner 增加互動感
    with st.spinner(f"正在分析股票 {stock_id}，請稍候..."):
        
        # --- 美化重點 3：使用 Tabs 分頁 (介面更乾淨) ---
        tab_chart, tab_info, tab_news = st.tabs(["📊 歷史走勢", "🔍 即時概況", "📰 相關新聞"])

        with tab_chart:
            st.subheader(f"yfinance 歷史趨勢圖 (最近 6 個月)")
            #             # --- 美化重點 4：yfinance 圖表與資料美化 ---
            target = f"{stock_id}.TW"
            df_yf = yf.download(target, period="6mo")
            if not df_yf.empty:
                # 畫出收盤價圖表
                st.line_chart(df_yf['Close'])
                
                # 美化 Dataframe 顯示
                st.write("### 最近 5 日詳細數據")
                # 使用簡潔的 table 呈現最近 5 天資料
                st.table(df_yf.tail().style.format("{:.2f}"))
            else:
                st.error("找不到該股票的歷史資料，請檢查代碼是否正確。")

        with tab_info:
            st.subheader("Yahoo 股市即時概況")
            df_yahoo = get_yahoo_data(stock_id)
            if df_yahoo is not None:
                # 對調表格讓它更符合網頁閱讀習慣
                st.table(df_yahoo.T)
            else:
                st.warning("Yahoo 資料抓取失敗，請稍後再試。")

        with tab_news:
            st.subheader("鉅亨網最新相關新聞")
            df_news = get_cnyes_news(stock_id)
            if not df_news.empty:
                # 用 markdown 的方式顯示新聞，看起來更簡潔
                for i, row in df_news.iterrows():
                    st.markdown(f"**[{row['日期']}]** [{row['標題']}]({row['連結']})")
            else:
                st.write("目前查無相關新聞。")

    st.success("🎉 全方位分析完成！")
else:
    # 預設顯示的畫面
    st.info("請在左側輸入股票代碼，然後按下上面的按鈕開始查詢。")
