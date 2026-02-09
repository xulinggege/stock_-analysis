import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import data_loader
import importlib
# 强制重新加载 data_loader，防止 Streamlit Cloud 缓存旧版本导致 AttributeError
importlib.reload(data_loader)
import json
import os

# --- 辅助函数：收藏管理 ---
FAV_FILE = 'favorites.json'

def load_favorites():
    if not os.path.exists(FAV_FILE):
        return []
    try:
        with open(FAV_FILE, 'r') as f:
            data = json.load(f)
            # Migration: convert list of strings to list of dicts
            if data and isinstance(data[0], str):
                new_data = []
                for code in data:
                    name = data_loader.get_stock_name(code)
                    new_data.append({'code': code, 'name': name})
                return new_data
            return data
    except:
        return []

def save_favorites(favorites):
    with open(FAV_FILE, 'w') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# 初始化 session state
if 'stock_code_input' not in st.session_state:
    st.session_state.stock_code_input = "600519"
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False

# 设置页面配置
st.set_page_config(
    page_title="A股股票分析",
    page_icon="📈",
    layout="wide"
)

# 加载收藏
favorites = load_favorites()

# --- 侧边栏配置 ---
st.sidebar.header("参数设置")

# 收藏夹功能区
with st.sidebar.expander("⭐ 我的收藏", expanded=True):
    if not favorites:
        st.write("暂无收藏")
    else:
        st.write("点击查看:")
        # 使用单列布局，避免文字换行
        for item in favorites:
            # 兼容旧数据（如果 load_favorites 迁移失败或手动修改过）
            if isinstance(item, str):
                code = item
                name = item
            else:
                code = item.get('code')
                name = item.get('name', code)
            
            label = f"{name} ({code})"
            if st.button(label, key=f"fav_{code}", use_container_width=True):
                st.session_state.stock_code_input = code
                st.session_state.run_analysis = True
                st.rerun()

st.sidebar.markdown("---")

# 股票代码输入
# 使用 key 绑定 session_state，这样可以通过代码更新输入框的值
stock_code = st.sidebar.text_input("股票代码", key="stock_code_input", help="请输入6位股票代码，如 600519")

# 检查是否已收藏
is_fav = False
for item in favorites:
    if isinstance(item, dict) and item.get('code') == stock_code:
        is_fav = True
        break
    elif isinstance(item, str) and item == stock_code: # 兼容旧数据
        is_fav = True
        break

# 添加/取消收藏按钮
if is_fav:
    if st.sidebar.button("💔 取消收藏", use_container_width=True):
        # 移除逻辑
        favorites = [f for f in favorites if (isinstance(f, dict) and f['code'] != stock_code) or (isinstance(f, str) and f != stock_code)]
        save_favorites(favorites)
        st.rerun()
else:
    if st.sidebar.button("❤️ 添加收藏", use_container_width=True):
        if stock_code and len(stock_code) == 6:
            # 获取名称并保存
            name = data_loader.get_stock_name(stock_code)
            favorites.append({'code': stock_code, 'name': name})
            save_favorites(favorites)
            st.rerun()
        else:
            st.sidebar.warning("请输入有效的6位代码")

# 日期范围选择
today = datetime.now()
half_year_ago = today - timedelta(days=180)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("开始日期", value=half_year_ago)
with col2:
    end_date = st.date_input("结束日期", value=today)

# 分析按钮逻辑
# 如果点击了“开始分析”或者通过点击收藏触发了自动分析
start_btn = st.sidebar.button("开始分析", type="primary")

if start_btn or st.session_state.run_analysis:
    # 重置自动运行标志，防止刷新页面后重复运行（虽然 st.button 本身不保持状态，但为了逻辑清晰）
    if st.session_state.run_analysis:
        st.session_state.run_analysis = False
        
    with st.spinner(f"正在获取 {stock_code} 的数据并生成图表..."):
        # 格式化日期为 YYYYMMDD
        s_date_str = start_date.strftime('%Y%m%d')
        e_date_str = end_date.strftime('%Y%m%d')
        
        # 获取数据
        try:
            df = data_loader.get_stock_data(stock_code, s_date_str, e_date_str)
            
            if df.empty:
                st.error(f"未获取到股票 {stock_code} 的数据，请检查代码或日期范围。")
            else:
                # 获取股票名称
                stock_name = data_loader.get_stock_name(stock_code)

                # 页面主标题
                st.title(f"📈 {stock_name} ({stock_code}) 股价与换手率分析")
                
                # 创建子图：K线图 (row=1) 和 换手率图 (row=2)
                fig = make_subplots(
                    rows=2, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3],
                    subplot_titles=('K线图 (K-Line)', '换手率 (Turnover Rate)')
                )

                # 1. 绘制 K 线图
                # 计算移动平均线
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA10'] = df['Close'].rolling(window=10).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()

                # K线
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='K线'
                ), row=1, col=1)

                # 均线
                fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='blue', width=1), name='MA5'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], line=dict(color='orange', width=1), name='MA10'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='green', width=1), name='MA20'), row=1, col=1)

                # 2. 绘制换手率图
                # 颜色区分：上涨红，下跌绿 (中国习惯：红涨绿跌)
                colors = ['red' if row['Close'] >= row['Open'] else 'green' for i, row in df.iterrows()]
                
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['Turnover'],
                    name='换手率',
                    marker_color=colors
                ), row=2, col=1)

                # 更新布局
                fig.update_layout(
                    height=800,
                    xaxis_rangeslider_visible=False,
                    title_text=f"{stock_name} ({stock_code}) - {start_date} 至 {end_date}",
                    hovermode='x unified' # 统一显示 hover 信息
                )
                
                # 更新坐标轴标签
                fig.update_yaxes(title_text="价格", row=1, col=1)
                fig.update_yaxes(title_text="换手率 (%)", row=2, col=1)

                # 在 Streamlit 中展示 Plotly 图表
                st.plotly_chart(fig, use_container_width=True)

                # 展示原始数据 (可选)
                with st.expander("查看原始数据"):
                    st.dataframe(df.sort_index(ascending=False))

        except Exception as e:
            st.error(f"发生错误: {str(e)}")

else:
    st.info("请在左侧选择收藏股票或输入代码并点击“开始分析”。")
